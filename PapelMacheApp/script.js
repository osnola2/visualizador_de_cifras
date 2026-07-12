const chordData = {
    "F7M9": {
        name: "F7M(9)",
        notes: ["F3", "A3", "C4", "E4", "G4"],
        displayNotes: ["F", "A", "C", "E", "G"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "Dm7911": {
        name: "Dm7(9/11)",
        notes: ["D3", "F3", "A3", "C4", "E4", "G4"],
        displayNotes: ["D", "F", "A", "C", "E", "G"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth", "alt"]
    },
    "C7M5": {
        name: "C7M(5+)",
        notes: ["C3", "E3", "G#3", "B3"],
        displayNotes: ["C", "E", "G#", "B"],
        noteTypes: ["triad", "triad", "alt", "seventh"]
    },
    "A79": {
        name: "A7(9)",
        notes: ["A3", "C#4", "E4", "G4", "B4"],
        displayNotes: ["A", "C#", "E", "G", "B"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "A713": {
        name: "A7(13-)",
        notes: ["A3", "C#4", "E4", "G4", "F4"],
        displayNotes: ["A", "C#", "E", "G", "F"],
        noteTypes: ["triad", "triad", "triad", "seventh", "alt"]
    },
    "Fm79": {
        name: "Fm7(9)",
        notes: ["F3", "G#3", "C4", "D#4", "G4"],
        displayNotes: ["F", "Ab", "C", "Eb", "G"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "G7913": {
        name: "G7(9/13)",
        notes: ["G3", "B3", "D4", "F4", "A4", "E4"],
        displayNotes: ["G", "B", "D", "F", "A", "E"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth", "alt"]
    },
    "Db759": {
        name: "Db7(5+/9+)",
        notes: ["C#3", "F3", "A3", "D#4"],
        displayNotes: ["Db", "F", "A", "Eb"],
        noteTypes: ["triad", "triad", "alt", "ninth"]
    },
    "C7M": {
        name: "C7M",
        notes: ["C3", "E3", "G3", "B3"],
        displayNotes: ["C", "E", "G", "B"],
        noteTypes: ["triad", "triad", "triad", "seventh"]
    },
    "C7MB": {
        name: "C7M/B",
        notes: ["B3", "C4", "E4", "G4"],
        displayNotes: ["B", "C", "E", "G"],
        noteTypes: ["seventh", "triad", "triad", "triad"]
    },
    "Am79": {
        name: "Am7(9)",
        notes: ["A3", "C4", "E4", "G4", "B4"],
        displayNotes: ["A", "C", "E", "G", "B"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "D7911": {
        name: "D7(9/11+)",
        notes: ["D3", "F#3", "A3", "C4", "E4", "G#4"],
        displayNotes: ["D", "F#", "A", "C", "E", "G#"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth", "alt"]
    },
    "A79p13m": {
        name: "A7(9+/13-)",
        notes: ["A3", "C#4", "F4", "G4", "C4"],
        displayNotes: ["A", "C#", "F", "G", "C"],
        noteTypes: ["triad", "triad", "alt", "seventh", "ninth"]
    },
    "A79m13": {
        name: "A7(9-/13)",
        notes: ["A3", "C#4", "G4", "A#4", "F#4"],
        displayNotes: ["A", "C#", "G", "Bb", "F#"],
        noteTypes: ["triad", "triad", "seventh", "ninth", "alt"]
    },
    "D7913": {
        name: "D7(9/13)",
        notes: ["D3", "F#3", "C4", "E4", "B4"],
        displayNotes: ["D", "F#", "C", "E", "B"],
        noteTypes: ["triad", "triad", "seventh", "ninth", "alt"]
    },
    "C749": {
        name: "C7(4/9)",
        notes: ["C3", "F3", "G3", "A#3", "D4"],
        displayNotes: ["C", "F", "G", "Bb", "D"],
        noteTypes: ["triad", "alt", "triad", "seventh", "ninth"]
    },
    "Am7M": {
        name: "Am7M",
        notes: ["A3", "C4", "E4", "G#4"],
        displayNotes: ["A", "C", "E", "G#"],
        noteTypes: ["triad", "triad", "triad", "seventh"]
    },
    "Em7911": {
        name: "Em7(9/11)",
        notes: ["E3", "G3", "B3", "D4", "F#4", "A4"],
        displayNotes: ["E", "G", "B", "D", "F#", "A"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth", "alt"]
    },
    "E69m": {
        name: "E6(9-)",
        notes: ["E3", "G#3", "B3", "C#4", "F4"],
        displayNotes: ["E", "G#", "B", "C#", "F"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "E713": {
        name: "E7(13-)",
        notes: ["E3", "G#3", "D4", "C4"],
        displayNotes: ["E", "G#", "D", "C"],
        noteTypes: ["triad", "triad", "seventh", "alt"]
    },
    "Bb79": {
        name: "Bb7(9)",
        notes: ["A#3", "D4", "F4", "G#4", "C4"],
        displayNotes: ["Bb", "D", "F", "Ab", "C"],
        noteTypes: ["triad", "triad", "triad", "seventh", "ninth"]
    },
    "Db79p": {
        name: "Db7(9+)",
        notes: ["C#3", "F3", "B3", "E4"],
        displayNotes: ["Db", "F", "B", "E"],
        noteTypes: ["triad", "triad", "seventh", "ninth"]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const nextChordVisualizer = window.NextChordVisualizer
        ? new window.NextChordVisualizer({ containerId: 'next-chord-section' })
        : null;
    if (nextChordVisualizer) {
        nextChordVisualizer.mount('next-chord-section');
    }

    const chordElements = document.querySelectorAll('.chord');
    const titleElement = document.getElementById('current-chord-name');
    const pillsContainer = document.getElementById('chord-notes-container');
    
    // Store all piano keys by note name
    const keys = {};
    document.querySelectorAll('.key').forEach(key => {
        keys[key.dataset.note] = key;
    });

    let currentTriadVoicingIndex = 0;
    let currentDisplayedChordId = 'G7M';
    let currentNextChordId = null;
    let currentNextLyric = null;

    const invButtons = document.querySelectorAll('#current-inversion-controls .inv-side-btn');
    invButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            invButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTriadVoicingIndex = parseInt(btn.getAttribute('data-inv'), 10) || 0;
            showChord(currentDisplayedChordId, currentNextChordId, currentNextLyric);
        });
    });

    const noteMap = { 'C':0, 'C#':1, 'Db':1, 'D':2, 'D#':3, 'Eb':3, 'E':4, 'F':5, 'F#':6, 'Gb':6, 'G':7, 'G#':8, 'Ab':8, 'A':9, 'A#':10, 'Bb':10, 'B':11 };
    const revMap = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];

    function noteToMidi(noteStr) {
        const octave = parseInt(noteStr.slice(-1), 10);
        const name = noteStr.slice(0, -1);
        return (octave - 3) * 12 + noteMap[name];
    }

    function midiToNote(midi) {
        const octave = Math.floor(midi / 12) + 3;
        const name = revMap[midi % 12];
        return `${name}${octave}`;
    }

    function applyInversionToNotes(notes, invIdx) {
        if (!notes || notes.length === 0 || invIdx === 0) return notes;
        let midiList = notes.map(n => ({ note: n, midi: noteToMidi(n) })).sort((a,b) => a.midi - b.midi);
        for (let s = 0; s < invIdx && s < 3; s++) {
            if (midiList.length > 0 && midiList[0].midi + 12 <= 23) {
                const low = midiList[0];
                midiList = midiList.slice(1).concat([{ note: midiToNote(low.midi + 12), midi: low.midi + 12 }]);
            }
        }
        if (invIdx === 3 && midiList.length >= 3) {
            const mid = midiList[1];
            if (mid.midi + 12 <= 23) {
                midiList[1] = { note: midiToNote(mid.midi + 12), midi: mid.midi + 12 };
            }
        }
        return midiList.map(m => m.note);
    }

    function resetPiano() {
        document.querySelectorAll('.piano-keyboard .key').forEach(k => {
            k.className = k.className.replace(/active|next-active|next-key|triad|seventh|ninth|alt/g, '').trim();
            k.textContent = '';
        });
        const notesContainer = document.getElementById('chord-notes-container');
        if (notesContainer) notesContainer.innerHTML = '';
        if (nextChordVisualizer) nextChordVisualizer.clearKeys();
        if (titleElement) {
            titleElement.textContent = "Toque ou passe o mouse";
            titleElement.style.opacity = '0.7';
        }
    }

    function showChord(chordName, nextChordName, nextLyric = null) {
        resetPiano();
        const data = chordData[chordName];
        if (!data) return;

        currentDisplayedChordId = chordName;
        currentNextChordId = nextChordName || null;
        currentNextLyric = nextLyric || null;
        
        const chordTitle = document.getElementById('current-chord-name');
        const notesContainer = document.getElementById('chord-notes-container');

        if (chordTitle) {
            chordTitle.textContent = data.name;
            chordTitle.style.opacity = '1';
        }

        const voicedNotes = applyInversionToNotes(data.notes, currentTriadVoicingIndex);
        let currentVoicedForNext = [];

        voicedNotes.forEach((note, index) => {
            const type = data.noteTypes ? data.noteTypes[index] : 'triad';
            const keyEl = document.querySelector(`#piano-current .key[data-note="${note}"]`);
            if (keyEl) {
                keyEl.classList.add('active', type);
                keyEl.textContent = data.displayNotes[index] || note.slice(0, -1);
            }
            if (notesContainer) {
                const pill = document.createElement('span');
                pill.className = `note-pill active ${type}`;
                pill.textContent = data.displayNotes[index] || note.slice(0, -1);
                notesContainer.appendChild(pill);
            }
            currentVoicedForNext.push({
                note,
                displayNote: data.displayNotes[index] || note.slice(0, -1),
                type
            });
        });

        if (nextChordVisualizer) {
            if (nextChordName && chordData[nextChordName]) {
                const nextData = chordData[nextChordName];
                nextChordVisualizer.renderChord(nextData.name, nextData, nextChordVisualizer.currentInversionIndex, currentVoicedForNext, currentNextLyric);
            } else {
                nextChordVisualizer.renderChord('---', null, 0, null, null);
            }
        }
    }

    // Karaoke Mode: Split lyrics into lines
    const lyricsContent = document.getElementById('lyrics-content');
    const rawLines = lyricsContent.innerHTML.split('\n');
    let lastChord = null;

    lyricsContent.innerHTML = rawLines.map(line => {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = line;
        const chordsInLine = tempDiv.querySelectorAll('.chord');
        
        if (chordsInLine.length > 0) {
            lastChord = chordsInLine[0].dataset.chord;
        }

        return `<div class="lyric-line" data-associated-chord="${lastChord || ''}">${line}</div>`;
    }).join('');

    function getLyricForChordElement(chordEl) {
        if (!chordEl) return null;
        const parentLine = chordEl.closest('.lyric-line');
        let lyricEl = parentLine ? parentLine.nextElementSibling : null;
        return lyricEl ? lyricEl.textContent.trim() : null;
    }

    // Re-select chord elements if we want to keep hover (optional)
    const newChordElements = document.querySelectorAll('.chord');
    newChordElements.forEach(chord => {
        chord.addEventListener('mouseenter', (e) => {
            resetPiano();
            const idxInSong = allChords.findIndex(c => c.element === chord);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(e.target.dataset.chord, nextData, nextLyric);
            if (typeof highlightRightPanelLyric === 'function') highlightRightPanelLyric(chord);
        });
        chord.addEventListener('click', (e) => {
            resetPiano();
            const idxInSong = allChords.findIndex(c => c.element === chord);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(e.target.dataset.chord, nextData, nextLyric);
            if (typeof highlightRightPanelLyric === 'function') highlightRightPanelLyric(chord);
        });
    });

    // Removed IntersectionObserver for text lines. Lyric highlighting is now driven by chords.

    // Initialize with opacity 0.5
    titleElement.style.opacity = '0.5';

    // Advanced Chord Tracking (Sequential even on same line)
    // We map all chords and assign them an 'effectiveY'.
    // Chords on the left get a slightly smaller effectiveY, so they trigger first as we scroll down.
    let allChords = [];
    setTimeout(() => {
        // Group chords by their vertical position (same line)
        const chordsByLine = {};
        Array.from(document.querySelectorAll('.chord')).forEach(chord => {
            const rect = chord.getBoundingClientRect();
            // Round to nearest 10 to ensure chords on the same visual line are grouped together
            const absoluteTop = Math.round((rect.top + window.scrollY) / 10) * 10;
            
            if (!chordsByLine[absoluteTop]) chordsByLine[absoluteTop] = [];
            chordsByLine[absoluteTop].push({
                element: chord,
                chordName: chord.dataset.chord,
                absoluteLeft: rect.left + window.scrollX,
                exactTop: rect.top + window.scrollY
            });
        });

        const lineTops = Object.keys(chordsByLine).map(Number).sort((a, b) => a - b);
        
        for (let i = 0; i < lineTops.length; i++) {
            const currentTop = lineTops[i];
            // Calculate available scroll space until the next chord line (default to 80px for the last line)
            const nextTop = i < lineTops.length - 1 ? lineTops[i+1] : currentTop + 80;
            const availableSpace = nextTop - currentTop; 
            
            const chords = chordsByLine[currentTop];
            // Sort chords on this line from left to right
            chords.sort((a, b) => a.absoluteLeft - b.absoluteLeft);
            
            for (let j = 0; j < chords.length; j++) {
                // Distribute chords evenly across the vertical scroll space between lines
                // We multiply by 0.8 to ensure the last chord triggers a bit before the next line begins
                const fraction = j / chords.length; 
                const yOffset = fraction * availableSpace * 0.8; 
                
                allChords.push({
                    element: chords[j].element,
                    chordName: chords[j].chordName,
                    effectiveY: chords[j].exactTop + yOffset
                });
            }
        }
        allChords.sort((a, b) => a.effectiveY - b.effectiveY);
        
        // Trigger initial check so the first chord highlights immediately
        window.dispatchEvent(new Event('scroll'));
    }, 500); // Wait a bit for layout to settle

    function highlightRightPanelLyric(activeChordEl) {
        const displayChord = document.getElementById('active-display-chord');
        const displayLyric = document.getElementById('active-display-lyric');
        if (!activeChordEl || !displayChord || !displayLyric) return;

        const parentLine = activeChordEl.closest('.lyric-line') || activeChordEl.parentElement;
        let lyricEl = parentLine ? parentLine.nextElementSibling : null;

        const lyricText = lyricEl ? lyricEl.textContent.trim() : "Intro / Instrumental";
        displayLyric.textContent = lyricText || "---";

        const activeRect = activeChordEl.getBoundingClientRect();
        const allChords = Array.from(document.querySelectorAll('.chord'));
        const chordsOnLine = allChords.filter(c => {
            const r = c.getBoundingClientRect();
            return Math.abs(r.top - activeRect.top) < 28;
        }).sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);

        if (chordsOnLine.length <= 1) {
            displayChord.innerHTML = activeChordEl.textContent.trim();
        } else {
            const sequenceHtml = chordsOnLine.map(c => {
                const name = c.textContent.trim();
                const isActive = (c === activeChordEl);
                if (isActive) {
                    return `<span style="background: #fbbf24; color: #0f172a; padding: 3px 12px; border-radius: 8px; font-weight: 800; box-shadow: 0 0 15px rgba(251, 191, 36, 0.7); transform: scale(1.12); display: inline-block;">${name}</span>`;
                } else {
                    return `<span style="opacity: 0.5; font-weight: 600; padding: 2px 6px;">${name}</span>`;
                }
            }).join(`<span style="opacity: 0.35; margin: 0 6px;">→</span>`);
            displayChord.innerHTML = sequenceHtml;
        }

    }

    let currentPlayingChordEl = null;
    window.addEventListener('scroll', () => {
        if (allChords.length === 0) return;
        
        let activeChordData = null;
        if (window.scrollY < 40) {
            activeChordData = allChords[0];
        } else {
            const readingY = window.scrollY + 320;
            for (let i = 0; i < allChords.length; i++) {
                if (readingY >= allChords[i].effectiveY) {
                    activeChordData = allChords[i];
                } else {
                    break;
                }
            }
        }
        
        // If we haven't reached the first chord yet, default to the very first one
        if (!activeChordData && allChords.length > 0) {
            activeChordData = allChords[0];
        }
        
        if (activeChordData && activeChordData.element !== currentPlayingChordEl) {
            currentPlayingChordEl = activeChordData.element;
            resetPiano();
            const idxInSong = allChords.indexOf(activeChordData);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(activeChordData.chordName, nextData, nextLyric);
            
            // Highlight chord
            document.querySelectorAll('.chord.active-chord').forEach(c => c.classList.remove('active-chord'));
            activeChordData.element.classList.add('active-chord');

            // Highlight the lyric line corresponding to this chord
            document.querySelectorAll('.lyric-line.active-line').forEach(el => el.classList.remove('active-line'));
            const parentLine = activeChordData.element.closest('.lyric-line');
            if (parentLine && parentLine.nextElementSibling) {
                parentLine.nextElementSibling.classList.add('active-line');
            }

            highlightRightPanelLyric(activeChordData.element);
        }
    }, { passive: true });

    // Keyboard Navigation for Chords
    window.addEventListener('keydown', (e) => {
        if (allChords.length === 0) return;
        
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault(); // Prevent default browser scrolling
            
            const readingY = window.scrollY + window.innerHeight * 0.45;
            let currentIndex = 0;
            
            // Find the currently active chord index
            for (let i = 0; i < allChords.length; i++) {
                if (readingY >= allChords[i].effectiveY - 2) { 
                    currentIndex = i;
                } else {
                    break;
                }
            }
            
            let nextIndex = currentIndex;
            if (e.key === 'ArrowDown') {
                nextIndex = Math.min(currentIndex + 1, allChords.length - 1);
            } else if (e.key === 'ArrowUp') {
                // If we are slightly past the current chord but still on it, going up should go to the previous one
                // If we are exactly on it, going up goes to previous. 
                nextIndex = Math.max(currentIndex - 1, 0);
            }
            
            const targetY = allChords[nextIndex].effectiveY - window.innerHeight * 0.45 + 5;
            window.scrollTo({
                top: Math.max(0, targetY),
                behavior: 'smooth'
            });
        }
    });

    // Smooth Auto-scroll
    const autoscrollBtn = document.getElementById('autoscroll-btn');
    const speedSlider = document.getElementById('speed-slider');
    const speedLabel = document.getElementById('speed-label');
    const bpmInput = document.getElementById('bpm-input');
    
    let isAutoScrolling = false;
    let animationFrameId = null;
    let scrollAccumulator = 0;

    // Update label when slider changes
    speedSlider.addEventListener('input', () => {
        const val = parseFloat(speedSlider.value);
        speedLabel.textContent = `Ajuste: ${val.toFixed(1)}x`;
    });

    function autoScrollStep() {
        if (!isAutoScrolling) return;
        
        const allLyrics = document.querySelectorAll('.lyric-line');
        const lastLyric = allLyrics.length > 0 ? allLyrics[allLyrics.length - 1] : null;
        if (lastLyric) {
            const rect = lastLyric.getBoundingClientRect();
            if (rect.top <= 300) {
                if (isAutoScrolling) {
                    autoscrollBtn.click();
                }
                return;
            }
        } else if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
            if (isAutoScrolling) {
                autoscrollBtn.click();
            }
            return;
        }

        // Base speed for 100 BPM is 0.4 pixels per frame
        const bpmRatio = parseInt(bpmInput.value) / 100;
        const baseSpeed = 0.4 * bpmRatio;
        
        const currentSpeed = parseFloat(speedSlider.value) * baseSpeed;
        scrollAccumulator += currentSpeed;
        
        if (scrollAccumulator >= 1) {
            const pixels = Math.floor(scrollAccumulator);
            window.scrollBy({ top: pixels, behavior: 'instant' });
            scrollAccumulator -= pixels;
        }
        
        animationFrameId = requestAnimationFrame(autoScrollStep);
    }

    autoscrollBtn.addEventListener('click', () => {
        isAutoScrolling = !isAutoScrolling;
        
        if (isAutoScrolling) {
            autoscrollBtn.classList.add('active');
            autoscrollBtn.innerHTML = '<span class="icon">⏸</span> Pause Auto-scroll';
            autoScrollStep();
        } else {
            autoscrollBtn.classList.remove('active');
            autoscrollBtn.innerHTML = '<span class="icon">▶</span> Auto-scroll';
            cancelAnimationFrame(animationFrameId);
        }
    });

});

document.addEventListener('DOMContentLoaded', () => {

    // Toggle Piano Logic
    const togglePianoBtn = document.getElementById('toggle-piano-btn');
    if (togglePianoBtn) {
        togglePianoBtn.addEventListener('click', () => {
            const panel = document.querySelector('.piano-panel');
            if (panel) {
                panel.classList.toggle('piano-hidden');
                if (panel.classList.contains('piano-hidden')) {
                    togglePianoBtn.style.opacity = '0.5';
                } else {
                    togglePianoBtn.style.opacity = '1';
                }
            }
        });
    }

});
