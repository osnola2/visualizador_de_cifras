let chordData = {};

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');

    if (!songId) {
        document.getElementById('song-title-el').textContent = 'Nenhuma música selecionada';
        document.getElementById('song-artist-el').textContent = '';
        return;
    }

    let isLoaded = false;
    function loadSongData() {
        if (isLoaded) return;
        if (!window.SONG_DATA) {
            document.getElementById('song-title-el').textContent = 'Erro ao carregar';
            document.getElementById('song-artist-el').textContent = 'Dados da música não encontrados.';
            return;
        }
        isLoaded = true;
        const data = window.SONG_DATA;
        document.getElementById('song-title-el').textContent = data.title;
        document.getElementById('song-artist-el').textContent = data.artist;
        document.getElementById('lyrics-content').innerHTML = data.lyricsHtml;
        chordData = data.chordData || {};
        
        initViewer();
    }

    const scriptEl = document.createElement('script');
    scriptEl.onload = loadSongData;
    scriptEl.onerror = () => {
        if (!isLoaded) {
            document.getElementById('song-title-el').textContent = 'Erro ao carregar';
            document.getElementById('song-artist-el').textContent = 'Arquivo da música não encontrado no catálogo.';
        }
    };
    scriptEl.src = `data/songs/${songId}.js`;
    document.head.appendChild(scriptEl);

    // Fallback de segurança para carregamento em protocolo file://
    const checkInterval = setInterval(() => {
        if (window.SONG_DATA && !isLoaded) {
            clearInterval(checkInterval);
            loadSongData();
        }
    }, 40);
    setTimeout(() => clearInterval(checkInterval), 4000);
});

function initViewer() {
    const nextChordVisualizer = window.NextChordVisualizer
        ? new window.NextChordVisualizer({ containerId: 'next-chord-section' })
        : null;
    if (nextChordVisualizer) {
        nextChordVisualizer.mount('next-chord-section');
    }

    const keys = document.querySelectorAll('.key');
    const chordTitle = document.getElementById('current-chord-name');
    const notesContainer = document.getElementById('chord-notes-container');
    const chordElements = document.querySelectorAll('.chord');

    let currentTriadVoicingIndex = 0;
    let currentTensionVoicingIndex = 0;
    let currentDisplayedChordId = null;
    let currentNextChordId = null;
    let currentNextLyric = null;
    let currentInstrument = 'piano';

    const btnPiano = document.getElementById('btn-inst-piano');
    const btnGuitar = document.getElementById('btn-inst-guitar');
    const pianoRow = document.getElementById('piano-view-row');
    const guitarCurrentView = document.getElementById('guitar-current-view');
    const nextPianoSection = document.getElementById('next-chord-section');
    const guitarNextView = document.getElementById('guitar-next-view');

    function setInstrument(inst) {
        currentInstrument = inst;
        if (btnPiano && btnGuitar) {
            if (inst === 'piano') {
                btnPiano.classList.add('active');
                btnPiano.style.background = 'var(--primary)';
                btnPiano.style.color = '#0f172a';
                btnGuitar.classList.remove('active');
                btnGuitar.style.background = 'transparent';
                btnGuitar.style.color = '#cbd5e1';
                if (pianoRow) pianoRow.style.display = 'flex';
                if (nextPianoSection) nextPianoSection.style.display = 'block';
                if (guitarCurrentView) guitarCurrentView.style.display = 'none';
                if (guitarNextView) guitarNextView.style.display = 'none';
            } else {
                btnGuitar.classList.add('active');
                btnGuitar.style.background = 'var(--primary)';
                btnGuitar.style.color = '#0f172a';
                btnPiano.classList.remove('active');
                btnPiano.style.background = 'transparent';
                btnPiano.style.color = '#cbd5e1';
                if (pianoRow) pianoRow.style.display = 'none';
                if (nextPianoSection) nextPianoSection.style.display = 'none';
                if (guitarCurrentView) guitarCurrentView.style.display = 'block';
                if (guitarNextView) guitarNextView.style.display = 'block';
            }
        }
        if (currentDisplayedChordId) {
            showChord(currentDisplayedChordId, currentNextChordId, currentNextLyric);
        }
    }

    if (btnPiano) btnPiano.addEventListener('click', () => setInstrument('piano'));
    if (btnGuitar) btnGuitar.addEventListener('click', () => setInstrument('guitar'));

    const triadVoicingNames = ["Padrão", "1ª Inversão", "2ª Inversão"];
    const tensionVoicingNames = ["Padrão", "Agudo (+8ª)", "Grave (-8ª)"];

    const voicingTriadLabels = document.querySelectorAll('.voicing-triad-label');
    const voicingTensionLabels = document.querySelectorAll('.voicing-tension-label');

    const headerVoicingTriadBtn = document.getElementById('header-voicing-triad-btn');
    const pianoVoicingTriadBtn = document.getElementById('piano-voicing-triad-btn');
    const headerVoicingTensionBtn = document.getElementById('header-voicing-tension-btn');
    const pianoVoicingTensionBtn = document.getElementById('piano-voicing-tension-btn');

    function toggleTriadVoicing() {
        currentTriadVoicingIndex = (currentTriadVoicingIndex + 1) % 3;
        voicingTriadLabels.forEach(lbl => lbl.textContent = triadVoicingNames[currentTriadVoicingIndex]);
        if (currentDisplayedChordId) showChord(currentDisplayedChordId, currentNextChordId);
    }

    function toggleTensionVoicing() {
        currentTensionVoicingIndex = (currentTensionVoicingIndex + 1) % 3;
        voicingTensionLabels.forEach(lbl => lbl.textContent = tensionVoicingNames[currentTensionVoicingIndex]);
        if (currentDisplayedChordId) showChord(currentDisplayedChordId, currentNextChordId);
    }

    if (headerVoicingTriadBtn) headerVoicingTriadBtn.addEventListener('click', toggleTriadVoicing);
    if (pianoVoicingTriadBtn) pianoVoicingTriadBtn.addEventListener('click', toggleTriadVoicing);
    if (headerVoicingTensionBtn) headerVoicingTensionBtn.addEventListener('click', toggleTensionVoicing);
    if (pianoVoicingTensionBtn) pianoVoicingTensionBtn.addEventListener('click', toggleTensionVoicing);
    
    let currentNextChordId = null;
    let currentNextLyric = null;

    function getLyricForChordElement(chordEl) {
        if (!chordEl) return null;
        let curr = chordEl.nextSibling;
        let passedNewline = false;

        while (curr) {
            if (curr.nodeType === 1) {
                if (curr.classList.contains('lyric-line')) {
                    const txt = curr.textContent.trim();
                    if (txt) return txt;
                }
                if (curr.classList.contains('chord') && passedNewline) {
                    break;
                }
            } else if (curr.nodeType === 3) {
                const text = curr.nodeValue || '';
                if (text.includes('\n')) {
                    passedNewline = true;
                }
                const trimmed = text.trim();
                if (trimmed.length > 0) {
                    return trimmed;
                }
            }
            curr = curr.nextSibling;
        }
        return null;
    }

    const invButtons = document.querySelectorAll('#current-inversion-controls .inv-side-btn');
    invButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            invButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTriadVoicingIndex = parseInt(btn.getAttribute('data-inv'), 10) || 0;
            voicingTriadLabels.forEach(lbl => lbl.textContent = triadVoicingNames[currentTriadVoicingIndex] || "Padrão");
            if (currentDisplayedChordId) showChord(currentDisplayedChordId, currentNextChordId, currentNextLyric);
        });
    });

    function resetPiano() {
        document.querySelectorAll('.piano-keyboard .key').forEach(k => {
            k.className = k.className.replace(/active|next-active|next-key|triad|seventh|ninth|alt/g, '').trim();
            k.textContent = '';
        });
        const notesContainer = document.getElementById('chord-notes-container');
        const nextNotesContainer = document.getElementById('next-chord-notes-container');
        if (notesContainer) notesContainer.innerHTML = '';
        if (nextNotesContainer) nextNotesContainer.innerHTML = '';
        if (nextChordVisualizer) nextChordVisualizer.clearKeys();
    }

    function showChord(chordId, nextChordId, nextLyric = null) {
        resetPiano();
        const data = chordData[chordId];
        if (!data) return;

        currentDisplayedChordId = chordId;
        currentNextChordId = nextChordId || null;
        currentNextLyric = nextLyric || null;
        
        const chordTitle = document.getElementById('current-chord-name');
        const nextTitle = document.getElementById('next-chord-name');
        const notesContainer = document.getElementById('chord-notes-container');
        const nextNotesContainer = document.getElementById('next-chord-notes-container');

        if (chordTitle) chordTitle.textContent = data.name;

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

        function computeVoicedNotes(cData) {
            let items = cData.notes.map((note, index) => ({
                note,
                display: cData.displayNotes ? cData.displayNotes[index] : note.slice(0, -1),
                type: cData.noteTypes ? (cData.noteTypes[index] || 'triad') : 'triad'
            }));

            let triadItems = items
                .filter(it => ['root', 'triad'].includes(it.type))
                .map(it => ({ ...it, midi: noteToMidi(it.note) }))
                .sort((a, b) => a.midi - b.midi);

            let tensionItems = items
                .filter(it => !['root', 'triad', 'bass'].includes(it.type))
                .map(it => ({ ...it, midi: noteToMidi(it.note) }))
                .sort((a, b) => a.midi - b.midi);
                
            let bassItems = items
                .filter(it => it.type === 'bass')
                .map(it => ({ ...it, midi: noteToMidi(it.note) }))
                .sort((a, b) => a.midi - b.midi);

            for (let step = 0; step < currentTriadVoicingIndex && step < 3; step++) {
                if (triadItems.length > 0) {
                    const lowest = triadItems[0];
                    if (lowest.midi + 12 <= 23) {
                        triadItems = triadItems.slice(1).concat([{
                            ...lowest,
                            midi: lowest.midi + 12,
                            note: midiToNote(lowest.midi + 12)
                        }]);
                        triadItems.sort((a, b) => a.midi - b.midi);
                    } else {
                        const highest = triadItems[triadItems.length - 1];
                        if (highest.midi - 12 >= 0) {
                            triadItems = [{
                                ...highest,
                                midi: highest.midi - 12,
                                note: midiToNote(highest.midi - 12)
                            }].concat(triadItems.slice(0, -1));
                            triadItems.sort((a, b) => a.midi - b.midi);
                        }
                    }
                }
            }
            if (currentTriadVoicingIndex === 3 && triadItems.length >= 3) {
                const mid = triadItems[1];
                if (mid.midi + 12 <= 23) {
                    triadItems[1] = {
                        ...mid,
                        midi: mid.midi + 12,
                        note: midiToNote(mid.midi + 12)
                    };
                }
            }

            if (currentTensionVoicingIndex === 1 && tensionItems.length > 0) {
                tensionItems = tensionItems.map(item => {
                    const nextMidi = item.midi + 12;
                    return nextMidi <= 23 ? { ...item, midi: nextMidi, note: midiToNote(nextMidi) } : item;
                });
            } else if (currentTensionVoicingIndex === 2 && tensionItems.length > 0) {
                tensionItems = tensionItems.map(item => {
                    const prevMidi = item.midi - 12;
                    return prevMidi >= 0 ? { ...item, midi: prevMidi, note: midiToNote(prevMidi) } : item;
                });
            }

            return bassItems.concat(triadItems).concat(tensionItems);
        }

        const currentVoiced = computeVoicedNotes(data);
        currentVoiced.forEach(item => {
            const keyEl = document.querySelector(`#piano-current .key[data-note="${item.note}"]`);
            if (keyEl) {
                keyEl.classList.add('active', item.type);
                keyEl.textContent = item.display;
            }
        });

        if (nextChordVisualizer) {
            if (nextChordId && chordData[nextChordId]) {
                const nextData = chordData[nextChordId];
                nextChordVisualizer.renderChord(nextData.name, nextData, nextChordVisualizer.currentInversionIndex, currentVoiced, currentNextLyric);
            } else {
                nextChordVisualizer.renderChord('---', null, 0, null, null);
            }
        }

        if (window.GuitarChordVisualizer) {
            const gCurrEl = document.getElementById('guitar-current-view');
            const gNextEl = document.getElementById('guitar-next-view');
            if (gCurrEl) {
                gCurrEl.innerHTML = window.GuitarChordVisualizer.renderGuitarFretboardSVG(data.name);
            }
            if (gNextEl) {
                if (nextChordId && chordData[nextChordId]) {
                    const nextData = chordData[nextChordId];
                    gNextEl.innerHTML = `
                        <div style="display: flex; justify-content: center; align-items: center; margin: 0.2rem 0 0.2rem; gap: 8px;">
                            <span style="font-size: 0.65rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase;">🔵 Próximo:</span>
                            <span style="font-size: 0.95rem; color: #fff; font-weight: 700;">${nextData.name}</span>
                        </div>
                        ${window.GuitarChordVisualizer.renderGuitarFretboardSVG(nextData.name)}
                        ${nextLyric ? `<div style="text-align: center; font-size: 0.82rem; color: #cbd5e1; margin-top: 0.3rem; font-style: italic;">"${nextLyric}"</div>` : ''}
                    `;
                } else {
                    gNextEl.innerHTML = '';
                }
            }
        }
    }

    chordElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            const cId = el.getAttribute('data-chord');
            const idxInSong = allChords.findIndex(c => c.element === el);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(cId, nextData, nextLyric);
            if (typeof highlightRightPanelLyric === 'function') highlightRightPanelLyric(el);
        });

        el.addEventListener('click', () => {
            const cId = el.getAttribute('data-chord');
            const idxInSong = allChords.findIndex(c => c.element === el);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(cId, nextData, nextLyric);
            if (typeof highlightRightPanelLyric === 'function') highlightRightPanelLyric(el);
        });
    });

    let allChords = [];
    setTimeout(() => {
        const chordElementsList = Array.from(document.querySelectorAll('.chord'));
        let chordsByLine = {};
        let lineTops = [];
        
        chordElementsList.forEach(el => {
            const rect = el.getBoundingClientRect();
            const exactTop = rect.top + window.scrollY;
            const lineKey = Math.round(exactTop / 10) * 10;
            
            if (!chordsByLine[lineKey]) {
                chordsByLine[lineKey] = [];
                lineTops.push(lineKey);
            }
            chordsByLine[lineKey].push({
                element: el,
                chordName: el.getAttribute('data-chord'),
                exactTop: exactTop,
                absoluteLeft: rect.left + window.scrollX
            });
        });

        lineTops.sort((a, b) => a - b);

        for (let i = 0; i < lineTops.length; i++) {
            const currentTop = lineTops[i];
            const nextTop = i < lineTops.length - 1 ? lineTops[i+1] : currentTop + 80;
            const availableSpace = nextTop - currentTop; 
            
            const chords = chordsByLine[currentTop];
            chords.sort((a, b) => a.absoluteLeft - b.absoluteLeft);
            
            for (let j = 0; j < chords.length; j++) {
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
        window.dispatchEvent(new Event('scroll'));
    }, 400);

    function highlightRightPanelLyric(activeChordEl) {
        const displayChord = document.getElementById('active-display-chord');
        const displayLyric = document.getElementById('active-display-lyric');
        if (!activeChordEl || !displayChord || !displayLyric) return;

        const foundLyric = getLyricForChordElement(activeChordEl);
        const lyricText = foundLyric ? foundLyric : "Intro / Instrumental";
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
            
            document.querySelectorAll('.chord.active-chord').forEach(c => c.classList.remove('active-chord'));
            activeChordData.element.classList.add('active-chord');

            document.querySelectorAll('.lyric-line.active-line').forEach(el => el.classList.remove('active-line'));
            let curr = activeChordData.element.nextSibling;
            while (curr) {
                if (curr.nodeType === 1 && curr.classList.contains('lyric-line')) {
                    curr.classList.add('active-line');
                    break;
                }
                curr = curr.nextSibling;
            }

            highlightRightPanelLyric(activeChordData.element);
        }
    });


    // Keyboard Navigation for chords
    document.addEventListener('keydown', (e) => {
        if (typeof allChords === 'undefined' || allChords.length === 0) return;
        
        let currentIdx = allChords.findIndex(c => c.element === currentPlayingChordEl);
        if (currentIdx === -1) currentIdx = 0;

        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
            e.preventDefault();
            if (currentIdx < allChords.length - 1) {
                const nextY = allChords[currentIdx + 1].effectiveY - 319;
                window.scrollTo({ top: nextY, behavior: 'auto' });
            }
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
            e.preventDefault();
            if (currentIdx > 0) {
                const prevY = allChords[currentIdx - 1].effectiveY - 321;
                window.scrollTo({ top: prevY, behavior: 'auto' });
            }
        }
    });

    // Auto-scroll logic
    const autoscrollBtn = document.getElementById('autoscroll-btn');
    const speedSlider = document.getElementById('speed-slider');
    const speedLabel = document.getElementById('speed-label');
    const bpmInput = document.getElementById('bpm-input');
    
    let isAutoScrolling = false;
    let animationFrameId = null;
    let scrollAccumulator = 0;

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

}
