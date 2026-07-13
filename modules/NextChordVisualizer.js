/**
 * ============================================================================
 * NextChordVisualizer Module (modules/NextChordVisualizer.js)
 * ============================================================================
 * Módulo reutilizável para renderização e controle visual do próximo acorde
 * em um teclado de piano empilhado.
 * 
 * Compatível com inclusão via <script src="../modules/NextChordVisualizer.js">
 * (disponibilizando window.NextChordVisualizer) ou importação ES Module.
 */

(function (global, factory) {
    if (typeof exports === 'object' && typeof module !== 'undefined') {
        module.exports = factory();
    } else if (typeof define === 'function' && define.amd) {
        define(factory);
    } else {
        global.NextChordVisualizer = factory();
    }
})(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    // Definição das 24 teclas do teclado de piano (C3 a B4)
    const PIANO_KEYS_TEMPLATE = [
        // Oitava 3
        { note: 'C3', type: 'white' },
        { note: 'C#3', type: 'black', left: '4.8%' },
        { note: 'D3', type: 'white' },
        { note: 'D#3', type: 'black', left: '11.8%' },
        { note: 'E3', type: 'white' },
        { note: 'F3', type: 'white' },
        { note: 'F#3', type: 'black', left: '26%' },
        { note: 'G3', type: 'white' },
        { note: 'G#3', type: 'black', left: '33%' },
        { note: 'A3', type: 'white' },
        { note: 'A#3', type: 'black', left: '40.2%' },
        { note: 'B3', type: 'white' },
        // Oitava 4
        { note: 'C4', type: 'white' },
        { note: 'C#4', type: 'black', left: '54.8%' },
        { note: 'D4', type: 'white' },
        { note: 'D#4', type: 'black', left: '61.8%' },
        { note: 'E4', type: 'white' },
        { note: 'F4', type: 'white' },
        { note: 'F#4', type: 'black', left: '76%' },
        { note: 'G4', type: 'white' },
        { note: 'G#4', type: 'black', left: '83%' },
        { note: 'A4', type: 'white' },
        { note: 'A#4', type: 'black', left: '90.2%' },
        { note: 'B4', type: 'white' }
    ];

    const CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    class NextChordVisualizer {
        /**
         * @param {Object} options
         * @param {string} [options.containerId='next-chord-visualizer']
         * @param {string} [options.pianoId='piano-next']
         * @param {string} [options.titleId='next-chord-name']
         * @param {string} [options.notesId='next-chord-notes-container']
         */
        constructor(options = {}) {
            this.containerId = options.containerId || 'next-chord-visualizer';
            this.pianoId = options.pianoId || 'piano-next';
            this.titleId = options.titleId || 'next-chord-name';
            this.notesId = options.notesId || 'next-chord-notes-container';
            this.currentChordName = null;
            this.currentChordObj = null;
            this.currentInversionIndex = 0;
            this.previousChordData = null;
            this.nextLyric = null;
        }

        /**
         * Monta o DOM do visualizador do próximo acorde dentro de um elemento contêiner.
         * @param {HTMLElement|string} targetElement - Elemento DOM ou ID onde o visualizador será inserido
         */
        mount(targetElement) {
            const container = typeof targetElement === 'string'
                ? document.getElementById(targetElement)
                : targetElement;

            if (!container) {
                console.warn(`NextChordVisualizer: Elemento contêiner não encontrado.`);
                return;
            }

            // Gera as teclas HTML
            const keysHtml = PIANO_KEYS_TEMPLATE.map(k => {
                const styleAttr = k.left ? ` style="left: ${k.left};"` : '';
                return `<div class="key ${k.type}" data-note="${k.note}"${styleAttr}></div>`;
            }).join('');

            container.innerHTML = `
                <div class="next-chord-header" style="text-align: center; margin-top: 0.8rem;">
                    <span class="next-badge" style="background: rgba(245, 158, 11, 0.18); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); padding: 0.25rem 0.8rem; border-radius: 12px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                        🟡 Próximo Acorde
                    </span>
                    <h3 id="${this.titleId}" style="margin: 0.35rem 0 0.15rem 0; color: #f59e0b; font-size: 1.15rem; font-weight: 800;">---</h3>
                </div>
                <div class="piano-row">
                    <div id="${this.pianoId}" class="piano-keyboard">
                        ${keysHtml}
                    </div>
                    <div class="inversion-column next-inv" id="next-inversion-controls">
                        <button class="inv-side-btn active" data-inv="0">Padrão</button>
                        <button class="inv-side-btn" data-inv="1">1ª Inv</button>
                        <button class="inv-side-btn" data-inv="2">2ª Inv</button>
                        <button class="inv-side-btn" data-inv="3">Aberto</button>
                    </div>
                </div>
                <div id="${this.notesId}" class="next-chord-lyric" style="text-align: center; font-size: 1.02rem; font-style: italic; color: #fef08a; margin-top: 0.6rem; min-height: 1.6rem; padding: 0.35rem 0.65rem; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.25);">---</div>
            `;

            this.setupInversionListeners();
        }

        setupInversionListeners() {
            const controls = document.getElementById('next-inversion-controls');
            if (!controls) return;
            const buttons = controls.querySelectorAll('.inv-side-btn');
            buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.currentInversionIndex = parseInt(btn.dataset.inv, 10);
                    if (this.currentChordObj) {
                        this.renderChord(this.currentChordName, this.currentChordObj, this.currentInversionIndex, this.previousChordData, this.nextLyric);
                    }
                });
            });
        }

        /**
         * Limpa os destaques do teclado do próximo acorde
         */
        clearKeys() {
            const pianoEl = document.getElementById(this.pianoId);
            if (!pianoEl) return;
            const keys = pianoEl.querySelectorAll('.key');
            keys.forEach(k => {
                k.classList.remove('active', 'next-active', 'triad', 'seventh', 'ninth', 'alt', 'root', 'common-note');
                k.textContent = '';
            });
        }

        /**
         * Calcula as notas vozeadas (oitavadas) para o próximo acorde.
         */
        computeVoicedNotes(chordObj, inversionIndex = 0) {
            if (!chordObj || !chordObj.notes) return [];
            const rawNotes = chordObj.notes;
            const rawDisplayNotes = chordObj.displayNotes || rawNotes;
            const rawNoteTypes = chordObj.noteTypes || rawNotes.map(() => 'triad');
            const len = rawNotes.length;

            let rotatedNotes = [...rawNotes];
            let rotatedDisplayNotes = [...rawDisplayNotes];
            let rotatedNoteTypes = [...rawNoteTypes];

            if (len >= 3) {
                const shift = inversionIndex % len;
                rotatedNotes = [
                    ...rawNotes.slice(shift),
                    ...rawNotes.slice(0, shift)
                ];
                rotatedDisplayNotes = [
                    ...rawDisplayNotes.slice(shift),
                    ...rawDisplayNotes.slice(0, shift)
                ];
                rotatedNoteTypes = [
                    ...rawNoteTypes.slice(shift),
                    ...rawNoteTypes.slice(0, shift)
                ];
            }

            let voiced = [];
            let currentOctave = 3;
            let lastPitchClass = -1;

            rotatedNotes.forEach((noteName, idx) => {
                const baseNote = noteName.replace(/[0-9]/g, '');
                let pitchClass = CHROMATIC_SCALE.indexOf(baseNote);

                if (pitchClass !== -1) {
                    if (idx > 0 && pitchClass < lastPitchClass) {
                        currentOctave++;
                    }
                    if (currentOctave > 4) currentOctave = 4;
                    voiced.push({
                        note: `${baseNote}${currentOctave}`,
                        displayNote: rotatedDisplayNotes[idx] || baseNote,
                        type: rotatedNoteTypes[idx] || 'triad'
                    });
                    lastPitchClass = pitchClass;
                } else {
                    voiced.push({
                        note: noteName,
                        displayNote: rotatedDisplayNotes[idx] || noteName,
                        type: rotatedNoteTypes[idx] || 'triad'
                    });
                }
            });

            return voiced;
        }

        /**
         * Retorna o índice cromático (0-11) da nota ignorando oitava, lidando com enarmônicos.
         */
        getPitchClassIndex(noteStr) {
            if (!noteStr) return -1;
            const baseNote = noteStr.replace(/[0-9]/g, '').trim();
            const noteMap = {
                'C': 0, 'B#': 0,
                'C#': 1, 'Db': 1,
                'D': 2,
                'D#': 3, 'Eb': 3,
                'E': 4, 'Fb': 4,
                'F': 5, 'E#': 5,
                'F#': 6, 'Gb': 6,
                'G': 7,
                'G#': 8, 'Ab': 8,
                'A': 9,
                'A#': 10, 'Bb': 10,
                'B': 11, 'Cb': 11
            };
            return noteMap[baseNote] !== undefined ? noteMap[baseNote] : -1;
        }

        /**
         * Retorna o ID da tecla física no teclado (ex: '4_3' para E3, onde 4 é o pitchClassIndex e 3 é a oitava).
         */
        getPhysicalKeyId(noteStr) {
            if (!noteStr || typeof noteStr !== 'string') return null;
            const octave = noteStr.slice(-1);
            if (isNaN(octave)) return null;
            const pcIdx = this.getPitchClassIndex(noteStr);
            if (pcIdx === -1) return null;
            return `${pcIdx}_${octave}`;
        }

        /**
         * Exibe e destaca o próximo acorde no segundo teclado.
         * @param {string|null} chordName - Nome exibido do acorde
         * @param {Object|null} chordObj - Objeto com definições do acorde
         * @param {number} [inversionIndex=0] - Índice de inversão (0=padrão, 1=1ª inv, etc)
         * @param {Object|Array|null} [previousChordData=null] - Acorde anterior ou notas vozeadas para destacar a mesma tecla física em dourado claro
         * @param {string|null} [nextLyric=null] - Trecho da letra correspondente ao próximo acorde
         */
        renderChord(chordName, chordObj, inversionIndex = 0, previousChordData = null, nextLyric = null) {
            this.currentChordName = chordName;
            this.currentChordObj = chordObj;
            this.currentInversionIndex = inversionIndex;
            this.previousChordData = previousChordData;
            this.nextLyric = nextLyric;

            const controls = document.getElementById('next-inversion-controls');
            if (controls) {
                const buttons = controls.querySelectorAll('.inv-side-btn');
                buttons.forEach(b => {
                    b.classList.toggle('active', parseInt(b.dataset.inv, 10) === inversionIndex);
                });
            }

            this.clearKeys();

            const titleEl = document.getElementById(this.titleId);
            const notesContainerEl = document.getElementById(this.notesId);
            const pianoEl = document.getElementById(this.pianoId);

            if (!chordName || !chordObj) {
                this.currentChordName = null;
                if (titleEl) titleEl.textContent = chordName === null ? 'Fim da Música' : '---';
                if (notesContainerEl) notesContainerEl.textContent = '---';
                return;
            }

            this.currentChordName = chordName;
            if (titleEl) titleEl.textContent = chordName;

            // Mapeia identificadores de tecla física (pitchClassIndex_octave) do acorde anterior/atual
            const prevPhysicalKeys = new Set();
            let prevNotesList = [];
            if (Array.isArray(previousChordData)) {
                prevNotesList = previousChordData.map(item => typeof item === 'string' ? item : item.note);
            } else if (previousChordData && Array.isArray(previousChordData.notes)) {
                const prevVoiced = this.computeVoicedNotes(previousChordData, 0);
                prevNotesList = prevVoiced.map(item => item.note);
            }

            prevNotesList.forEach(n => {
                const keyId = this.getPhysicalKeyId(n);
                if (keyId) prevPhysicalKeys.add(keyId);
            });

            const voicedNotes = this.computeVoicedNotes(chordObj, inversionIndex);

            // Ilumina teclas com o mesmo padrão de cores de teoria musical do acorde principal e borda dourada para a mesma tecla mantida
            if (pianoEl) {
                voicedNotes.forEach(item => {
                    const keyEl = pianoEl.querySelector(`.key[data-note="${item.note}"]`);
                    if (keyEl) {
                        const itemKeyId = this.getPhysicalKeyId(item.note);
                        const isCommonKey = prevPhysicalKeys.size > 0 && itemKeyId && prevPhysicalKeys.has(itemKeyId);

                        keyEl.classList.add('active', item.type || 'triad');
                        if (isCommonKey) {
                            keyEl.classList.add('common-note');
                        }
                        keyEl.textContent = item.displayNote || item.note;
                    }
                });
            }

            // Exibe a continuação da letra do próximo acorde
            if (notesContainerEl) {
                notesContainerEl.textContent = nextLyric ? nextLyric : '---';
            }
        }
    }

    return NextChordVisualizer;
});
