let chordData = {};

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');

    // Atualiza o link de volta para o teclado mantendo a música selecionada
    const btnToPiano = document.getElementById('btn-to-piano');
    if (btnToPiano && songId) {
        btnToPiano.href = `viewer.html?song=${songId}`;
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
        document.getElementById('song-artist-el').textContent = data.artist;
        document.getElementById('lyrics-content').innerHTML = data.lyricsHtml;
        chordData = data.chordData || {};
        
        initViolaoViewer();
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

function initViolaoViewer() {
    let currentDisplayedChordId = null;
    let currentNextChordId = null;
    let currentNextLyric = null;

    const chordElements = document.querySelectorAll('.chord');
    const activeDisplayChord = document.getElementById('active-display-chord');
    const activeDisplayLyric = document.getElementById('active-display-lyric');
    const currentChordNameEl = document.getElementById('current-chord-name');
    const guitarCurrentView = document.getElementById('guitar-current-view');
    const guitarNextView = document.getElementById('guitar-next-view');

    function showChord(chordId, nextChordId, nextLyric) {
        if (!chordId || !chordData[chordId]) {
            if (activeDisplayChord) activeDisplayChord.textContent = '';
            if (activeDisplayLyric) activeDisplayLyric.textContent = 'Passe o mouse ou role a tela...';
            if (currentChordNameEl) currentChordNameEl.textContent = '---';
            if (guitarCurrentView) guitarCurrentView.innerHTML = '';
            if (guitarNextView) guitarNextView.innerHTML = '';
            return;
        }

        currentDisplayedChordId = chordId;
        currentNextChordId = nextChordId;
        currentNextLyric = nextLyric;

        const data = chordData[chordId];
        if (activeDisplayChord) activeDisplayChord.textContent = data.name;
        if (activeDisplayLyric) activeDisplayLyric.textContent = '';
        if (currentChordNameEl) currentChordNameEl.textContent = data.name;

        if (window.GuitarChordVisualizer && guitarCurrentView) {
            guitarCurrentView.innerHTML = window.GuitarChordVisualizer.renderGuitarFretboardSVG(data.name, { width: 220, height: 195 });
        }

        if (window.GuitarChordVisualizer && guitarNextView) {
            if (nextChordId && chordData[nextChordId]) {
                const nextData = chordData[nextChordId];
                guitarNextView.innerHTML = `
                    <div style="text-align: center; margin-bottom: 0.4rem;">
                        <span style="font-size: 1.05rem; font-weight: 800; color: #fff;">${nextData.name}</span>
                        ${nextLyric ? `<div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 0.2rem; font-style: italic;">"${nextLyric}"</div>` : ''}
                    </div>
                    ${window.GuitarChordVisualizer.renderGuitarFretboardSVG(nextData.name, { width: 180, height: 165 })}
                `;
            } else {
                guitarNextView.innerHTML = '<div style="text-align:center; color:#64748b; font-size:0.85rem; padding:1rem 0;">Fim da música</div>';
            }
        }
    }

    chordElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            if (!isAutoScrolling) {
                const chordId = el.getAttribute('data-chord');
                showChord(chordId, null, null);
            }
        });
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

        const effectiveBpm = baseBpm * speedMultiplier;
        const pixelsPerMinute = effectiveBpm * 15;
        const pixelsPerSecond = pixelsPerMinute / 60;
        const pixelsPerFrame = pixelsPerSecond / 60;

        scrollAccumulator += pixelsPerFrame;

        if (scrollAccumulator >= 1) {
            const pixels = Math.floor(scrollAccumulator);
            window.scrollBy({ top: pixels, behavior: 'instant' });
            scrollAccumulator -= pixels;
        }

        // Highlight center chord during autoscroll
        const viewportCenterY = window.innerHeight * 0.38;
        let closestChordEl = null;
        let minDistance = Infinity;
        let closestIndex = -1;

        chordElements.forEach((el, index) => {
            const rect = el.getBoundingClientRect();
            const elCenterY = rect.top + rect.height / 2;
            const distance = Math.abs(elCenterY - viewportCenterY);

            if (distance < minDistance) {
                minDistance = distance;
                closestChordEl = el;
                closestIndex = index;
            }
        });

        if (closestChordEl && minDistance < 250) {
            chordElements.forEach(el => el.classList.remove('active-chord'));
            closestChordEl.classList.add('active-chord');

            const chordId = closestChordEl.getAttribute('data-chord');
            let nextChordId = null;
            let nextLyricText = null;

            if (closestIndex !== -1 && closestIndex + 1 < chordElements.length) {
                const nextEl = chordElements[closestIndex + 1];
                nextChordId = nextEl.getAttribute('data-chord');

                let currNode = closestChordEl.nextSibling;
                let lyricCollected = '';
                while (currNode && currNode !== nextEl) {
                    if (currNode.nodeType === Node.TEXT_NODE) {
                        lyricCollected += currNode.textContent;
                    } else if (currNode.nodeType === Node.ELEMENT_NODE) {
                        if (currNode.classList && currNode.classList.contains('lyric-line')) {
                            lyricCollected += ' ' + currNode.textContent;
                        } else {
                            lyricCollected += ' ' + currNode.innerText;
                        }
                    }
                    currNode = currNode.nextSibling;
                }
                const cleaned = lyricCollected.replace(/\s+/g, ' ').trim();
                if (cleaned) {
                    nextLyricText = cleaned.length > 45 ? cleaned.substring(0, 45) + '...' : cleaned;
                }
            }

            if (chordId !== currentDisplayedChordId || nextChordId !== currentNextChordId) {
                showChord(chordId, nextChordId, nextLyricText);
            }
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
}
