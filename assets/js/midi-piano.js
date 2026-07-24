const START_NOTE = 21; // A0
const END_NOTE = 108;  // C8
const TOTAL_NOTES = END_NOTE - START_NOTE + 1;

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const IS_BLACK = [false, true, false, true, false, false, true, false, true, false, true, false];

const pianoContainer = document.getElementById("piano-keyboard");
const displayContainer = document.getElementById("note-display");

let activeNotes = new Set();
let keysMap = {}; // Maps midi note to DOM element

// Generate Keyboard
function initKeyboard() {
    let numWhiteKeys = 0;
    
    // First, count total white keys to calculate widths
    for (let i = START_NOTE; i <= END_NOTE; i++) {
        const noteIndex = i % 12;
        if (!IS_BLACK[noteIndex]) {
            numWhiteKeys++;
        }
    }

    const whiteKeyWidthPercent = 100 / numWhiteKeys;
    const blackKeyWidthPercent = whiteKeyWidthPercent * 0.7; // Black keys are slightly narrower

    let currentWhiteIndex = 0;

    for (let i = START_NOTE; i <= END_NOTE; i++) {
        const noteIndex = i % 12;
        const isBlack = IS_BLACK[noteIndex];
        const noteName = NOTE_NAMES[noteIndex];
        const octave = Math.floor(i / 12) - 1;

        const key = document.createElement("div");
        key.classList.add("key");
        key.dataset.note = i;
        key.dataset.name = noteName;

        if (isBlack) {
            key.classList.add("black");
            // Position exactly on the line between the previous and next white key
            key.style.width = `${blackKeyWidthPercent}%`;
            key.style.left = `${currentWhiteIndex * whiteKeyWidthPercent}%`;
        } else {
            key.classList.add("white");
            // Add label to C notes for orientation
            if (noteName === "C") {
                const label = document.createElement("div");
                label.classList.add("key-label");
                label.textContent = `C${octave}`;
                key.appendChild(label);
            }
            currentWhiteIndex++;
        }

        // Mouse events for testing without MIDI keyboard
        key.addEventListener('mousedown', () => { if(window.MidiDetector) window.MidiDetector.triggerNoteOn(i); });
        key.addEventListener('mouseup', () => { if(window.MidiDetector) window.MidiDetector.triggerNoteOff(i); });
        key.addEventListener('mouseleave', () => { if(window.MidiDetector) window.MidiDetector.triggerNoteOff(i); }); // prevent getting stuck

        pianoContainer.appendChild(key);
        keysMap[i] = key;
    }
}

// Update Top Display
function updateDisplay(sortedNotes, chordName) {
    displayContainer.innerHTML = "";
    
    if (chordName) {
        const chordLabel = document.createElement("div");
        chordLabel.style.color = "#2196F3";
        chordLabel.style.marginRight = "40px";
        chordLabel.textContent = chordName;
        displayContainer.appendChild(chordLabel);
    }
    
    sortedNotes.forEach(note => {
        const noteIndex = note % 12;
        const noteName = NOTE_NAMES[noteIndex];
        
        const label = document.createElement("div");
        label.textContent = noteName;
        displayContainer.appendChild(label);
    });
}

// Initialize
initKeyboard();
if (window.MidiDetector) {
    window.MidiDetector.init();
    window.MidiDetector.addListener((sortedNotes, chordName, changedNote, isNoteOn) => {
        if (changedNote !== undefined && keysMap[changedNote]) {
            if (isNoteOn) keysMap[changedNote].classList.add('active');
            else keysMap[changedNote].classList.remove('active');
        }
        updateDisplay(sortedNotes, chordName);
    });
} else {
    displayContainer.innerHTML = "<span style='font-size: 20px; color: #999;'>MidiDetector not loaded.</span>";
}
