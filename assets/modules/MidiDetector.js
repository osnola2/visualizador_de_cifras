window.MidiDetector = (function() {
    const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    const CHORDS_DICT = {
        '0,4,7': '',
        '0,3,7': 'm',
        '0,4,7,10': '7',
        '0,4,7,11': 'maj7',
        '0,3,7,10': 'm7',
        '0,3,6': 'dim',
        '0,3,6,9': 'dim7',
        '0,3,6,10': 'm7(b5)',
        '0,4,8': 'aug',
        '0,2,7': 'sus2',
        '0,5,7': 'sus4',
        '0,7': '5'
    };

    function detectChord(notesArray) {
        if (notesArray.length < 2) return null;
        let pitchClasses = [...new Set(notesArray.map(n => n % 12))];
        let bassNote = Math.min(...notesArray) % 12;
        
        for (let root of pitchClasses) {
            let intervals = pitchClasses.map(p => (p - root + 12) % 12).sort((a,b) => a-b);
            let key = intervals.join(',');
            if (CHORDS_DICT[key] !== undefined) {
                let chordName = NOTE_NAMES[root] + CHORDS_DICT[key];
                if (bassNote !== root) {
                    chordName += '/' + NOTE_NAMES[bassNote];
                }
                return chordName;
            }
        }
        return null;
    }

    let activeNotes = new Set();
    let listeners = [];

    function triggerNoteOn(note) {
        if (activeNotes.has(note)) return;
        activeNotes.add(note);
        notifyListeners(note, true);
    }

    function triggerNoteOff(note) {
        if (!activeNotes.has(note)) return;
        activeNotes.delete(note);
        notifyListeners(note, false);
    }

    function notifyListeners(changedNote, isNoteOn) {
        const sortedNotes = Array.from(activeNotes).sort((a, b) => a - b);
        const currentChord = detectChord(sortedNotes);
        listeners.forEach(cb => cb(sortedNotes, currentChord, changedNote, isNoteOn));
    }

    function onMIDIMessage(message) {
        const command = message.data[0];
        const note = message.data[1];
        const velocity = (message.data.length > 2) ? message.data[2] : 0;

        switch (command) {
            case 144: // noteOn
                if (velocity > 0) {
                    triggerNoteOn(note);
                } else {
                    triggerNoteOff(note);
                }
                break;
            case 128: // noteOff
                triggerNoteOff(note);
                break;
        }
    }

    let initialized = false;

    function initMIDI() {
        if (initialized) return;
        initialized = true;
        if (navigator.requestMIDIAccess) {
            navigator.requestMIDIAccess().then(
                midiAccess => {
                    const inputs = midiAccess.inputs.values();
                    for (let input = inputs.next(); input && !input.done; input = inputs.next()) {
                        input.value.onmidimessage = onMIDIMessage;
                    }
                    midiAccess.onstatechange = function(e) {
                        if (e.port.type === "input" && e.port.state === "connected") {
                            e.port.onmidimessage = onMIDIMessage;
                        }
                    };
                },
                err => console.warn("Failed to get MIDI access", err)
            );
        }
    }

    return {
        init: function() { initMIDI(); },
        addListener: function(cb) { listeners.push(cb); },
        removeListener: function(cb) { listeners = listeners.filter(l => l !== cb); },
        detectChord: detectChord,
        triggerNoteOn: triggerNoteOn,
        triggerNoteOff: triggerNoteOff,
        getActiveNotes: () => Array.from(activeNotes)
    };
})();
