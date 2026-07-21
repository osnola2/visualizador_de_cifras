let chordData = {};

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');

    // Atualiza os links de navegação entre instrumentos mantendo a música selecionada
    const btnToPiano = document.getElementById('btn-to-piano');
    if (btnToPiano && songId) {
        btnToPiano.href = `viewer.html?song=${songId}`;
    }
    const btnToGuitar = document.getElementById('btn-to-guitar');
    if (btnToGuitar && songId) {
        btnToGuitar.href = `viewer-violao.html?song=${songId}`;
    }

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
        if (data.composer && data.composer !== data.artist) {
            document.getElementById('song-artist-el').innerHTML = `${data.artist} <span style="font-size: 0.85em; opacity: 0.85; font-weight: 400;">(Comp: ${data.composer})</span>`;
        } else {
            document.getElementById('song-artist-el').textContent = data.artist;
        }
        document.getElementById('lyrics-content').innerHTML = data.lyricsHtml;
        chordData = data.chordData || {};
        
        initCavaquinhoViewer();
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

    const checkInterval = setInterval(() => {
        if (window.SONG_DATA && !isLoaded) {
            clearInterval(checkInterval);
            loadSongData();
        }
    }, 40);
    setTimeout(() => clearInterval(checkInterval), 4000);
});

function initCavaquinhoViewer() {
    let currentDisplayedChordId = null;
    let currentNextChordId = null;
    let currentNextLyric = null;
    let currentPlayingChordEl = null;

    const chordElements = document.querySelectorAll('.chord');
    const activeDisplayChord = document.getElementById('active-display-chord');
    const activeDisplayLyric = document.getElementById('active-display-lyric');
    const currentChordNameEl = document.getElementById('current-chord-name');
    const cavaquinhoCurrentView = document.getElementById('cavaquinho-current-view');
    const cavaquinhoNextView = document.getElementById('cavaquinho-next-view');

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

    function highlightRightPanelLyric(activeChordEl) {
        if (!activeChordEl || !activeDisplayChord || !activeDisplayLyric) return;

        const foundLyric = getLyricForChordElement(activeChordEl);
        const lyricText = foundLyric ? foundLyric : "Intro / Instrumental";
        activeDisplayLyric.textContent = lyricText || "---";

        const activeRect = activeChordEl.getBoundingClientRect();
        const allChordsList = Array.from(document.querySelectorAll('.chord'));
        const chordsOnLine = allChordsList.filter(c => {
            const r = c.getBoundingClientRect();
            return Math.abs(r.top - activeRect.top) < 28;
        }).sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);

        if (chordsOnLine.length <= 1) {
            activeDisplayChord.innerHTML = activeChordEl.textContent.trim();
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
            activeDisplayChord.innerHTML = sequenceHtml;
        }
    }

    function showChord(chordId, nextChordId, nextLyric) {
        if (!chordId || !chordData[chordId]) {
            if (currentChordNameEl) currentChordNameEl.textContent = '---';
            if (cavaquinhoCurrentView) cavaquinhoCurrentView.innerHTML = '';
            if (cavaquinhoNextView) cavaquinhoNextView.innerHTML = '';
            return;
        }

        currentDisplayedChordId = chordId;
        currentNextChordId = nextChordId || null;
        currentNextLyric = nextLyric || null;

        const data = chordData[chordId];
        if (currentChordNameEl) currentChordNameEl.textContent = data.name;

        const isMobile = window.innerWidth < 900;
        const svgW = isMobile ? 84 : 120;
        const svgH = isMobile ? 80 : 115;

        if (window.CavaquinhoChordVisualizer && cavaquinhoCurrentView) {
            cavaquinhoCurrentView.innerHTML = window.CavaquinhoChordVisualizer.renderCavaquinhoFretboardSVG(data.name, { width: svgW, height: svgH });
        }

        if (window.CavaquinhoChordVisualizer && cavaquinhoNextView) {
            if (nextChordId && chordData[nextChordId]) {
                const nextData = chordData[nextChordId];
                cavaquinhoNextView.innerHTML = `
                    <div style="text-align: center; margin-bottom: 0.15rem;">
                        <span style="font-size: ${isMobile ? '0.85rem' : '1.0rem'}; font-weight: 800; color: #fff;">${nextData.name}</span>
                        ${nextLyric ? `<div style="font-size: ${isMobile ? '0.7rem' : '0.78rem'}; color: #cbd5e1; margin-top: 0.1rem; font-style: italic;">"${nextLyric}"</div>` : ''}
                    </div>
                    ${window.CavaquinhoChordVisualizer.renderCavaquinhoFretboardSVG(nextData.name, { width: svgW, height: svgH })}
                `;
            } else {
                cavaquinhoNextView.innerHTML = '<div style="text-align:center; color:#64748b; font-size:0.85rem; padding:0.6rem 0;">Fim da música</div>';
            }
        }
    }

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

    chordElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            if (!isAutoScrolling) {
                const cId = el.getAttribute('data-chord');
                const idxInSong = allChords.findIndex(c => c.element === el);
                const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
                const nextData = nextItem ? nextItem.chordName : null;
                const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
                showChord(cId, nextData, nextLyric);
                highlightRightPanelLyric(el);
            }
        });

        el.addEventListener('click', () => {
            const cId = el.getAttribute('data-chord');
            const idxInSong = allChords.findIndex(c => c.element === el);
            const nextItem = (idxInSong >= 0 && idxInSong < allChords.length - 1) ? allChords[idxInSong + 1] : null;
            const nextData = nextItem ? nextItem.chordName : null;
            const nextLyric = nextItem ? getLyricForChordElement(nextItem.element) : null;
            showChord(cId, nextData, nextLyric);
            highlightRightPanelLyric(el);
        });
    });

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
    let speedMultiplier = 1.0;
    let baseBpm = 95;
    let animationFrameId;
    let scrollAccumulator = 0;

    if (speedSlider && speedLabel) {
        speedSlider.addEventListener('input', (e) => {
            speedMultiplier = parseFloat(e.target.value);
            speedLabel.textContent = `Ajuste: ${speedMultiplier.toFixed(1)}x`;
        });
    }

    if (bpmInput) {
        bpmInput.addEventListener('input', (e) => {
            const val = parseInt(e.target.value, 10);
            if (!isNaN(val) && val > 0) {
                baseBpm = val;
            }
        });
    }

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

        const effectiveBpm = bpmInput && !isNaN(parseInt(bpmInput.value)) ? parseInt(bpmInput.value) : baseBpm;
        const bpmRatio = effectiveBpm / 100;
        const baseSpeed = 0.4 * bpmRatio;
        const currentSpeed = speedMultiplier * baseSpeed;

        scrollAccumulator += currentSpeed;

        if (scrollAccumulator >= 1) {
            const pixels = Math.floor(scrollAccumulator);
            window.scrollBy({ top: pixels, behavior: 'instant' });
            scrollAccumulator -= pixels;
        }

        animationFrameId = requestAnimationFrame(autoScrollStep);
    }

    if (autoscrollBtn) {
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
    }

    // Toggle Cavaquinho Diagram Panel Logic
    const toggleCavaquinhoBtn = document.getElementById('toggle-cavaquinho-btn') || document.getElementById('toggle-guitar-btn') || document.getElementById('toggle-piano-btn');
    if (toggleCavaquinhoBtn) {
        toggleCavaquinhoBtn.addEventListener('click', () => {
            const panel = document.querySelector('.cavaquinho-panel') || document.querySelector('.piano-panel');
            if (panel) {
                panel.classList.toggle('cavaquinho-hidden');
                if (panel.classList.contains('cavaquinho-hidden')) {
                    toggleCavaquinhoBtn.style.opacity = '0.5';
                } else {
                    toggleCavaquinhoBtn.style.opacity = '1';
                }
            }
        });
    }

    // Live Transposition Module (-½ and +½ buttons)
    const transposeUpBtn = document.getElementById('transpose-up-btn');
    const transposeDownBtn = document.getElementById('transpose-down-btn');
    const transposeOffsetLabel = document.getElementById('transpose-offset-label');
    let currentTransposeOffset = 0;

    function transposeNote(noteStr, semitones, preferFlats = false) {
        const SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const FLATS  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
        let idx = SHARPS.indexOf(noteStr);
        if (idx === -1) idx = FLATS.indexOf(noteStr);
        if (idx === -1) {
            if (noteStr === 'Cb') idx = 11;
            else if (noteStr === 'E#') idx = 5;
            else if (noteStr === 'B#') idx = 0;
            else if (noteStr === 'Fb') idx = 4;
            else return noteStr;
        }
        let newIdx = (idx + semitones) % 12;
        if (newIdx < 0) newIdx += 12;
        return preferFlats ? FLATS[newIdx] : SHARPS[newIdx];
    }

    function transposeMidiNote(midiStr, semitones, preferFlats = false) {
        const octave = parseInt(midiStr.slice(-1), 10);
        if (isNaN(octave)) return transposeNote(midiStr, semitones, preferFlats);
        const name = midiStr.slice(0, -1);
        const SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const FLATS  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
        let idx = SHARPS.indexOf(name);
        if (idx === -1) idx = FLATS.indexOf(name);
        if (idx === -1) return midiStr;
        
        let totalMidi = (octave * 12) + idx + semitones;
        let newOctave = Math.floor(totalMidi / 12);
        let newIdx = totalMidi % 12;
        if (newIdx < 0) {
            newIdx += 12;
            newOctave -= 1;
        }
        const newName = preferFlats ? FLATS[newIdx] : SHARPS[newIdx];
        return `${newName}${newOctave}`;
    }

    function transposeChordSymbol(chordStr, semitones, preferFlats = false) {
        if (!chordStr || chordStr.trim() === '' || chordStr === '---') return chordStr;
        const parts = chordStr.split('/');
        const mainPart = parts[0];
        const bassPart = parts.length > 1 ? parts[1] : null;
        
        const rootMatch = mainPart.match(/^([CDEFGAB][#b]?)/);
        if (!rootMatch) return chordStr;
        
        const rootNote = rootMatch[1];
        const restOfChord = mainPart.slice(rootNote.length);
        const newRoot = transposeNote(rootNote, semitones, preferFlats);
        
        let newChord = newRoot + restOfChord;
        if (bassPart) {
            const bassMatch = bassPart.match(/^([CDEFGAB][#b]?)/);
            if (bassMatch) {
                const bassNote = bassMatch[1];
                const restOfBass = bassPart.slice(bassNote.length);
                const newBass = transposeNote(bassNote, semitones, preferFlats);
                newChord += '/' + newBass + restOfBass;
            } else {
                newChord += '/' + bassPart;
            }
        }
        return newChord;
    }

    function transposeCurrentSong(step) {
        currentTransposeOffset += step;
        const preferFlats = currentTransposeOffset < 0;
        
        if (transposeOffsetLabel) {
            if (currentTransposeOffset === 0) {
                transposeOffsetLabel.textContent = "Original";
            } else {
                const sign = currentTransposeOffset > 0 ? "+" : "";
                const halfSteps = currentTransposeOffset;
                if (halfSteps % 2 === 0) {
                    const tones = halfSteps / 2;
                    transposeOffsetLabel.textContent = `${sign}${tones} ${Math.abs(tones) === 1 ? 'tom' : 'tons'}`;
                } else {
                    transposeOffsetLabel.textContent = `${sign}${halfSteps} st`;
                }
            }
        }

        const chordElementsList = document.querySelectorAll('.chord');
        chordElementsList.forEach(el => {
            const oldChord = el.getAttribute('data-chord') || el.textContent.trim();
            const newChord = transposeChordSymbol(oldChord, step, preferFlats);
            el.setAttribute('data-chord', newChord);
            el.textContent = newChord;
        });

        if (typeof allChords !== 'undefined') {
            allChords.forEach(item => {
                if (item.element) {
                    item.chordName = item.element.getAttribute('data-chord') || item.element.textContent.trim();
                }
            });
        }

        const newChordData = {};
        for (const [oldName, data] of Object.entries(chordData)) {
            const newName = transposeChordSymbol(oldName, step, preferFlats);
            const newNotes = (data.notes || []).map(n => transposeMidiNote(n, step, preferFlats));
            const newDisplay = (data.displayNotes || (data.notes || []).map(n => n.replace(/[0-9]/g, ''))).map(dn => transposeNote(dn, step, preferFlats));
            newChordData[newName] = {
                name: newName,
                notes: newNotes,
                displayNotes: newDisplay,
                noteTypes: data.noteTypes || []
            };
        }
        chordData = newChordData;

        if (currentDisplayedChordId) {
            const newCurrentId = transposeChordSymbol(currentDisplayedChordId, step, preferFlats);
            const newNextId = currentNextChordId ? transposeChordSymbol(currentNextChordId, step, preferFlats) : null;
            showChord(newCurrentId, newNextId, currentNextLyric);
        } else if (typeof allChords !== 'undefined' && allChords.length > 0) {
            showChord(allChords[0].chordName, null, null);
        }
    }

    if (transposeUpBtn) {
        transposeUpBtn.addEventListener('click', () => transposeCurrentSong(1));
    }
    if (transposeDownBtn) {
        transposeDownBtn.addEventListener('click', () => transposeCurrentSong(-1));
    }

}
