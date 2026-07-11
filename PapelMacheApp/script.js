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
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const chordElements = document.querySelectorAll('.chord');
    const titleElement = document.getElementById('current-chord-name');
    const pillsContainer = document.getElementById('chord-notes-container');
    
    // Store all piano keys by note name
    const keys = {};
    document.querySelectorAll('.key').forEach(key => {
        keys[key.dataset.note] = key;
    });

    function resetPiano() {
        document.querySelectorAll('.key.active').forEach(key => {
            key.className = key.className.replace(/active|triad|seventh|ninth|alt/g, '').trim() + (key.dataset.note.includes('#') ? ' black' : ' white');
            key.textContent = ''; // Remove the letter
        });
        pillsContainer.innerHTML = '';
        titleElement.textContent = "Hover or scroll to play";
        titleElement.style.opacity = '0.5';
    }

    function showChord(chordName) {
        const data = chordData[chordName];
        if (!data) return;

        // Update Title
        titleElement.textContent = data.name;
        titleElement.style.opacity = '1';
        
        // Clear old pills
        pillsContainer.innerHTML = '';

        // Light up piano keys and add the note letter on top of the key
        data.notes.forEach((note, index) => {
            const type = data.noteTypes ? data.noteTypes[index] : 'triad';
            if (keys[note]) {
                keys[note].classList.add('active', type);
                keys[note].textContent = data.displayNotes[index]; // Shows the letter on the key
            }
            
            // Create pill
            const pill = document.createElement('span');
            pill.className = `note-pill active ${type}`;
            pill.textContent = data.displayNotes[index];
            pillsContainer.appendChild(pill);
        });
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

    // Re-select chord elements if we want to keep hover (optional)
    const newChordElements = document.querySelectorAll('.chord');
    newChordElements.forEach(chord => {
        chord.addEventListener('mouseenter', (e) => {
            resetPiano();
            showChord(e.target.dataset.chord);
        });
        chord.addEventListener('mouseleave', () => {
            // Wait for scroll to re-evaluate, or just reset
            const activeLine = document.querySelector('.lyric-line.active-line');
            if (activeLine && activeLine.dataset.associatedChord) {
                resetPiano();
                showChord(activeLine.dataset.associatedChord);
            } else {
                resetPiano();
            }
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

    let currentPlayingChord = null;
    window.addEventListener('scroll', () => {
        if (allChords.length === 0) return;
        const readingY = window.scrollY + window.innerHeight * 0.45; // reading line
        
        let activeChordData = null;
        for (let i = 0; i < allChords.length; i++) {
            if (readingY >= allChords[i].effectiveY) {
                activeChordData = allChords[i];
            } else {
                break;
            }
        }
        
        // If we haven't reached the first chord yet, default to the very first one
        if (!activeChordData && allChords.length > 0) {
            activeChordData = allChords[0];
        }
        
        if (activeChordData && activeChordData.chordName !== currentPlayingChord) {
            currentPlayingChord = activeChordData.chordName;
            resetPiano();
            showChord(activeChordData.chordName);
            
            // Highlight chord
            document.querySelectorAll('.chord.active-chord').forEach(c => c.classList.remove('active-chord'));
            activeChordData.element.classList.add('active-chord');

            // Highlight the lyric line corresponding to this chord
            document.querySelectorAll('.lyric-line.active-line').forEach(el => el.classList.remove('active-line'));
            const parentLine = activeChordData.element.closest('.lyric-line');
            
            const displayChord = document.getElementById('active-display-chord');
            const displayLyric = document.getElementById('active-display-lyric');
            
            if (parentLine) {
                // Highlight the line right after the chord line (which contains the lyrics)
                const lyricLine = parentLine.nextElementSibling;
                if (lyricLine) {
                    lyricLine.classList.add('active-line');
                    displayChord.textContent = activeChordData.element.textContent;
                    displayLyric.textContent = lyricLine.textContent.trim() || "---";
                } else {
                    displayChord.textContent = activeChordData.element.textContent;
                    displayLyric.textContent = "---";
                }
            }
        }
    }, { passive: true });

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

    // Pause scroll if user interacts manually (wheel or touch)
    const pauseScroll = (e) => {
        // Don't pause if interacting with controls
        if (e.target.closest('.controls-panel')) return;
        
        if (isAutoScrolling) {
            autoscrollBtn.click(); // toggle off
        }
    };
    window.addEventListener('wheel', pauseScroll, { passive: true });
    window.addEventListener('touchstart', pauseScroll, { passive: true });
});
