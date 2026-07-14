/**
 * ============================================================================
 * GuitarChordVisualizer Module (assets/modules/GuitarChordVisualizer.js)
 * ============================================================================
 * Módulo front-end independente para renderização visual de acordes no braço
 * do violão (fretboard) em SVG.
 */

(function (global, factory) {
    if (typeof exports === 'object' && typeof module !== 'undefined') {
        module.exports = factory();
    } else if (typeof define === 'function' && define.amd) {
        define(factory);
    } else {
        global.GuitarChordVisualizer = factory();
    }
})(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    // Dicionário front-end de shapes de violão (ordem das cordas: E6, A5, D4, G3, B2, E1)
    // -1 = X (corda abafada), 0 = corda solta, 1..14 = casa
    const CHORD_SHAPES = {
        // Maiores / Básicos
        'C': { frets: [-1, 3, 2, 0, 1, 0], baseFret: 1 },
        'D': { frets: [-1, -1, 0, 2, 3, 2], baseFret: 1 },
        'E': { frets: [0, 2, 2, 1, 0, 0], baseFret: 1 },
        'F': { frets: [1, 3, 3, 2, 1, 1], baseFret: 1, barre: 1 },
        'G': { frets: [3, 2, 0, 0, 0, 3], baseFret: 1 },
        'A': { frets: [-1, 0, 2, 2, 2, 0], baseFret: 1 },
        'B': { frets: [-1, 2, 4, 4, 4, 2], baseFret: 2, barre: 2 },
        'Bb': { frets: [-1, 1, 3, 3, 3, 1], baseFret: 1, barre: 1 },
        'Eb': { frets: [-1, 6, 8, 8, 8, 6], baseFret: 6, barre: 6 },
        'Ab': { frets: [4, 6, 6, 5, 4, 4], baseFret: 4, barre: 4 },
        'C#': { frets: [-1, 4, 6, 6, 6, 4], baseFret: 4, barre: 4 },
        'Db': { frets: [-1, 4, 6, 6, 6, 4], baseFret: 4, barre: 4 },
        'D#': { frets: [-1, 6, 8, 8, 8, 6], baseFret: 6, barre: 6 },
        'F#': { frets: [2, 4, 4, 3, 2, 2], baseFret: 2, barre: 2 },
        'Gb': { frets: [2, 4, 4, 3, 2, 2], baseFret: 2, barre: 2 },
        'G#': { frets: [4, 6, 6, 5, 4, 4], baseFret: 4, barre: 4 },
        'A#': { frets: [-1, 1, 3, 3, 3, 1], baseFret: 1, barre: 1 },

        // Menores
        'Cm': { frets: [-1, 3, 5, 5, 4, 3], baseFret: 3, barre: 3 },
        'Dm': { frets: [-1, -1, 0, 2, 3, 1], baseFret: 1 },
        'Em': { frets: [0, 2, 2, 0, 0, 0], baseFret: 1 },
        'Fm': { frets: [1, 3, 3, 1, 1, 1], baseFret: 1, barre: 1 },
        'Gm': { frets: [3, 5, 5, 3, 3, 3], baseFret: 3, barre: 3 },
        'Am': { frets: [-1, 0, 2, 2, 1, 0], baseFret: 1 },
        'Bm': { frets: [-1, 2, 4, 4, 3, 2], baseFret: 2, barre: 2 },
        'C#m': { frets: [-1, 4, 6, 6, 5, 4], baseFret: 4, barre: 4 },
        'Dbm': { frets: [-1, 4, 6, 6, 5, 4], baseFret: 4, barre: 4 },
        'D#m': { frets: [-1, 6, 8, 8, 7, 6], baseFret: 6, barre: 6 },
        'Ebm': { frets: [-1, 6, 8, 8, 7, 6], baseFret: 6, barre: 6 },
        'F#m': { frets: [2, 4, 4, 2, 2, 2], baseFret: 2, barre: 2 },
        'Gbm': { frets: [2, 4, 4, 2, 2, 2], baseFret: 2, barre: 2 },
        'G#m': { frets: [4, 6, 6, 4, 4, 4], baseFret: 4, barre: 4 },
        'Abm': { frets: [4, 6, 6, 4, 4, 4], baseFret: 4, barre: 4 },
        'A#m': { frets: [-1, 1, 3, 3, 2, 1], baseFret: 1, barre: 1 },
        'Bbm': { frets: [-1, 1, 3, 3, 2, 1], baseFret: 1, barre: 1 },

        // Sétimas da Dominante (7)
        'C7': { frets: [-1, 3, 2, 3, 1, 0], baseFret: 1 },
        'D7': { frets: [-1, -1, 0, 2, 1, 2], baseFret: 1 },
        'E7': { frets: [0, 2, 0, 1, 0, 0], baseFret: 1 },
        'F7': { frets: [1, 3, 1, 2, 1, 1], baseFret: 1, barre: 1 },
        'G7': { frets: [3, 2, 0, 0, 0, 1], baseFret: 1 },
        'A7': { frets: [-1, 0, 2, 0, 2, 0], baseFret: 1 },
        'B7': { frets: [-1, 2, 1, 2, 0, 2], baseFret: 1 },
        'C#7': { frets: [-1, 4, 6, 4, 6, 4], baseFret: 4, barre: 4 },
        'Db7': { frets: [-1, 4, 6, 4, 6, 4], baseFret: 4, barre: 4 },
        'D#7': { frets: [-1, 6, 8, 6, 8, 6], baseFret: 6, barre: 6 },
        'Eb7': { frets: [-1, 6, 8, 6, 8, 6], baseFret: 6, barre: 6 },
        'F#7': { frets: [2, 4, 2, 3, 2, 2], baseFret: 2, barre: 2 },
        'Gb7': { frets: [2, 4, 2, 3, 2, 2], baseFret: 2, barre: 2 },
        'G#7': { frets: [4, 6, 4, 5, 4, 4], baseFret: 4, barre: 4 },
        'Ab7': { frets: [4, 6, 4, 5, 4, 4], baseFret: 4, barre: 4 },
        'A#7': { frets: [-1, 1, 3, 1, 3, 1], baseFret: 1, barre: 1 },
        'Bb7': { frets: [-1, 1, 3, 1, 3, 1], baseFret: 1, barre: 1 },

        // Sétimas Maiores (7M / maj7)
        'C7M': { frets: [-1, 3, 2, 0, 0, 0], baseFret: 1 },
        'D7M': { frets: [-1, -1, 0, 2, 2, 2], baseFret: 1 },
        'E7M': { frets: [0, 2, 1, 1, 0, 0], baseFret: 1 },
        'F7M': { frets: [-1, -1, 3, 2, 1, 0], baseFret: 1 },
        'G7M': { frets: [3, 2, 0, 0, 0, 2], baseFret: 1 },
        'A7M': { frets: [-1, 0, 2, 1, 2, 0], baseFret: 1 },
        'B7M': { frets: [-1, 2, 4, 3, 4, 2], baseFret: 2, barre: 2 },
        'C#7M': { frets: [-1, 4, 6, 5, 6, 4], baseFret: 4, barre: 4 },
        'Db7M': { frets: [-1, 4, 6, 5, 6, 4], baseFret: 4, barre: 4 },
        'D#7M': { frets: [-1, 6, 8, 7, 8, 6], baseFret: 6, barre: 6 },
        'Eb7M': { frets: [-1, 6, 8, 7, 8, 6], baseFret: 6, barre: 6 },
        'F#7M': { frets: [2, -1, 3, 3, 2, -1], baseFret: 2 },
        'Gb7M': { frets: [2, -1, 3, 3, 2, -1], baseFret: 2 },
        'G#7M': { frets: [4, -1, 5, 5, 4, -1], baseFret: 4 },
        'Ab7M': { frets: [4, -1, 5, 5, 4, -1], baseFret: 4 },
        'A#7M': { frets: [-1, 1, 3, 2, 3, 1], baseFret: 1, barre: 1 },
        'Bb7M': { frets: [-1, 1, 3, 2, 3, 1], baseFret: 1, barre: 1 },

        // Menores com 7 (m7)
        'Cm7': { frets: [-1, 3, 5, 3, 4, 3], baseFret: 3, barre: 3 },
        'Dm7': { frets: [-1, -1, 0, 2, 1, 1], baseFret: 1 },
        'Em7': { frets: [0, 2, 2, 0, 3, 0], baseFret: 1 },
        'Fm7': { frets: [1, 3, 1, 1, 1, 1], baseFret: 1, barre: 1 },
        'F#m7': { frets: [2, 4, 2, 2, 2, 2], baseFret: 2, barre: 2 },
        'Gbm7': { frets: [2, 4, 2, 2, 2, 2], baseFret: 2, barre: 2 },
        'Gm7': { frets: [3, 5, 3, 3, 3, 3], baseFret: 3, barre: 3 },
        'G#m7': { frets: [4, 6, 4, 4, 4, 4], baseFret: 4, barre: 4 },
        'Abm7': { frets: [4, 6, 4, 4, 4, 4], baseFret: 4, barre: 4 },
        'Am7': { frets: [-1, 0, 2, 0, 1, 0], baseFret: 1 },
        'Bm7': { frets: [-1, 2, 4, 2, 3, 2], baseFret: 2, barre: 2 },
        'C#m7': { frets: [-1, 4, 6, 4, 5, 4], baseFret: 4, barre: 4 },
        'Dbm7': { frets: [-1, 4, 6, 4, 5, 4], baseFret: 4, barre: 4 },
        'D#m7': { frets: [-1, 6, 8, 6, 7, 6], baseFret: 6, barre: 6 },
        'Ebm7': { frets: [-1, 6, 8, 6, 7, 6], baseFret: 6, barre: 6 },
        'A#m7': { frets: [-1, 1, 3, 1, 2, 1], baseFret: 1, barre: 1 },
        'Bbm7': { frets: [-1, 1, 3, 1, 2, 1], baseFret: 1, barre: 1 },

        // Meio-diminutos / m7(5-) e Diminutos / dim7
        'Cm7(5-)': { frets: [-1, 3, 4, 3, 4, -1], baseFret: 3 },
        'C#m7(5-)': { frets: [-1, 4, 5, 4, 5, -1], baseFret: 4 },
        'Dm7(5-)': { frets: [-1, -1, 0, 1, 1, 1], baseFret: 1 },
        'D#m7(5-)': { frets: [-1, 6, 7, 6, 7, -1], baseFret: 6 },
        'Em7(5-)': { frets: [0, 1, 2, 0, 3, 0], baseFret: 1 },
        'Fm7(5-)': { frets: [1, -1, 1, 1, 0, -1], baseFret: 1 },
        'F#m7(5-)': { frets: [2, -1, 2, 2, 1, -1], baseFret: 1 },
        'Gm7(5-)': { frets: [3, -1, 3, 3, 2, -1], baseFret: 1 },
        'G#m7(5-)': { frets: [4, -1, 4, 4, 3, -1], baseFret: 3 },
        'Am7(5-)': { frets: [-1, 0, 1, 2, 1, 3], baseFret: 1 },
        'Bm7(5-)': { frets: [-1, 2, 3, 2, 3, -1], baseFret: 1 },
        'G#dim7': { frets: [4, -1, 3, 4, 3, -1], baseFret: 3 },
        'Bdim7': { frets: [-1, 2, 3, 1, 3, -1], baseFret: 1 },

        // Suspensos / 4/7 / 6 / m6 e Acordes Específicos
        'C4/7': { frets: [-1, 3, 3, 3, 1, -1], baseFret: 1 },
        'C#4/7': { frets: [-1, 4, 6, 4, 7, 4], baseFret: 4, barre: 4 },
        'D4/7': { frets: [-1, -1, 0, 2, 1, 3], baseFret: 1 },
        'D#4/7': { frets: [-1, 6, 8, 6, 9, 6], baseFret: 6, barre: 6 },
        'E4/7': { frets: [0, 2, 0, 2, 0, 0], baseFret: 1 },
        'F4/7': { frets: [1, 3, 1, 3, 1, 1], baseFret: 1, barre: 1 },
        'F#4/7': { frets: [2, 4, 2, 4, 2, 2], baseFret: 2, barre: 2 },
        'G4/7': { frets: [3, 3, 0, 0, 1, 1], baseFret: 1 },
        'A4/7': { frets: [-1, 0, 2, 0, 3, 0], baseFret: 1 },
        'B4/7': { frets: [-1, 2, 2, 2, 0, 2], baseFret: 1 },
        'C6': { frets: [-1, 3, 2, 2, 1, 0], baseFret: 1 },
        'D6': { frets: [-1, -1, 0, 2, 0, 2], baseFret: 1 },
        'E6': { frets: [0, 2, 2, 1, 2, 0], baseFret: 1 },
        'F6': { frets: [1, 3, 3, 2, 3, 1], baseFret: 1 },
        'F#6': { frets: [2, -1, 1, 3, 2, -1], baseFret: 1 },
        'G6': { frets: [3, 2, 0, 0, 0, 0], baseFret: 1 },
        'A6': { frets: [-1, 0, 2, 2, 2, 2], baseFret: 1 },
        'B6': { frets: [-1, 2, 4, 1, 4, -1], baseFret: 1 },
        'G#m6': { frets: [4, -1, 3, 4, 4, -1], baseFret: 3 },
        'Em6': { frets: [0, 2, 2, 0, 2, 0], baseFret: 1 },
        'Em6/G': { frets: [3, -1, 2, 0, 2, 0], baseFret: 1 },
        'B/A': { frets: [-1, 0, 4, 4, 4, -1], baseFret: 1 },
        'B7M(9)/F#': { frets: [2, -1, 1, 3, 2, -1], baseFret: 1 },
        'F7(11+)': { frets: [1, -1, 1, 2, 0, -1], baseFret: 1 },
        'E7M(13)': { frets: [0, -1, 1, 1, 2, -1], baseFret: 1 },
        'B7M(9)': { frets: [-1, 2, 1, 3, 2, -1], baseFret: 1 },
        'B6(9)/F': { frets: [1, -1, 1, 1, 2, -1], baseFret: 1 },
        'B6(9)': { frets: [-1, 2, 1, 1, 2, -1], baseFret: 1 },
        'B7(9)': { frets: [-1, 2, 1, 2, 2, -1], baseFret: 1 },
        'F/D#': { frets: [-1, 6, 7, 5, 6, -1], baseFret: 5 },
        'D/C': { frets: [-1, 3, 4, 2, 3, -1], baseFret: 2 },
        'Bb9/F': { frets: [1, -1, 0, 1, 1, -1], baseFret: 1 },
        'B7(13)': { frets: [-1, 2, 1, 2, 4, -1], baseFret: 1 },
        'D#/B': { frets: [-1, 2, 1, 3, 4, -1], baseFret: 1 },
        'C/B': { frets: [-1, 2, 2, 0, 1, 0], baseFret: 1 },
        'D/F#': { frets: [2, 0, 0, 2, 3, 2], baseFret: 1 },
        'E/G#': { frets: [4, -1, 2, 4, 5, -1], baseFret: 2 },
        'F/A': { frets: [-1, 0, 3, 2, 1, 1], baseFret: 1 },
        'G/B': { frets: [-1, 2, 0, 0, 0, 3], baseFret: 1 },
        'A/C#': { frets: [-1, 4, 2, 2, 2, -1], baseFret: 1 },
        'Bm/A': { frets: [-1, 0, 4, 4, 3, 2], baseFret: 2 }
    };

    /**
     * Resolve heurística de forma de acorde caso não esteja explícito no dicionário
     */
    function resolveChordShape(chordName) {
        if (!chordName || chordName === '---') return null;
        if (CHORD_SHAPES[chordName]) return CHORD_SHAPES[chordName];

        // Normalizar enharmônicos e verificar novamente se existe exato
        const normalized = chordName
            .replace(/^Db/, 'C#')
            .replace(/^Eb/, 'D#')
            .replace(/^Gb/, 'F#')
            .replace(/^Ab/, 'G#')
            .replace(/^Bb/, 'A#');
        if (CHORD_SHAPES[normalized]) return CHORD_SHAPES[normalized];

        // Se for um acorde invertido / com baixo no formato X/Y, tentar primeiro no dicionário, depois pegar só o acorde base X
        const baseChord = chordName.includes('/') ? chordName.split('/')[0] : chordName;
        if (CHORD_SHAPES[baseChord]) return CHORD_SHAPES[baseChord];

        const rootMatch = baseChord.match(/^[A-G][#b]?/);
        if (!rootMatch) return null;
        const root = rootMatch[0];

        const enharmonicMap = { 'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#', 'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb' };
        const altRoot = enharmonicMap[root] || root;

        const check = (suffix) => CHORD_SHAPES[root + suffix] || CHORD_SHAPES[altRoot + suffix];

        if (baseChord.includes('m7(5-)') || baseChord.includes('m7b5') || baseChord.includes('°') || baseChord.includes('dim')) {
            return check('m7(5-)') || check('dim7') || check('m7') || check('m') || check('');
        }
        if (baseChord.includes('dim7')) {
            return check('dim7') || check('m7(5-)') || check('m7') || check('m') || check('');
        }
        if (baseChord.includes('m7') || baseChord.includes('m9') || baseChord.includes('m11') || baseChord.includes('m13')) {
            return check('m7') || check('m') || check('');
        }
        if (baseChord.includes('7M') || baseChord.includes('maj7')) {
            return check('7M') || check('') || check('7');
        }
        if (baseChord.includes('4/7') || baseChord.includes('sus4') || baseChord.includes('7(4)')) {
            return check('4/7') || check('7') || check('');
        }
        if (baseChord.includes('7')) {
            return check('7') || check('');
        }
        if (baseChord.includes('m6')) {
            return check('m6') || check('m7') || check('m') || check('');
        }
        if (baseChord.includes('m')) {
            return check('m') || check('');
        }
        if (baseChord.includes('6')) {
            return check('6') || check('') || check('7M');
        }

        return check('') || null;
    }

    /**
     * Renderiza o SVG do braço do violão
     */
    function renderGuitarFretboardSVG(chordName, options = {}) {
        const shape = resolveChordShape(chordName);
        const width = options.width || 190;
        const height = options.height || 185;
        const numFrets = 4;

        if (!shape) {
            return `
                <div style="width: 100%; height: ${height}px; display: flex; align-items: center; justify-content: center; background: rgba(15, 23, 42, 0.4); border-radius: 8px; border: 1px dashed rgba(255,255,255,0.15);">
                    <span style="color: #94a3b8; font-size: 0.85rem;">Acorde ${chordName || '---'}</span>
                </div>
            `;
        }

        const frets = shape.frets;
        const baseFret = shape.baseFret || 1;
        const barre = shape.barre || null;

        const startX = 35;
        const endX = 165;
        const stringSpacing = (endX - startX) / 5;
        const topY = 40;
        const fretSpacing = 32;

        let svg = `<svg viewBox="0 0 ${width} ${height}" style="width: 100%; max-width: ${width}px; height: auto; display: block; margin: 0 auto; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));">`;

        // Indicador de casa (ex: 3ª casa)
        if (baseFret > 1) {
            svg += `<text x="12" y="${topY + fretSpacing * 0.6}" fill="#38bdf8" font-size="12" font-family="'Outfit', sans-serif" font-weight="700">${baseFret}ª</text>`;
        }

        // Pestana (nut) ou traço superior
        const nutStrokeWidth = baseFret === 1 ? 5 : 2;
        const nutColor = baseFret === 1 ? '#e2e8f0' : '#475569';
        svg += `<line x1="${startX}" y1="${topY}" x2="${endX}" y2="${topY}" stroke="${nutColor}" stroke-width="${nutStrokeWidth}" stroke-linecap="round" />`;

        // Trastes horizontais
        for (let i = 1; i <= numFrets; i++) {
            const y = topY + i * fretSpacing;
            svg += `<line x1="${startX}" y1="${y}" x2="${endX}" y2="${y}" stroke="#475569" stroke-width="1.5" />`;
        }

        // 6 Cordas verticais
        for (let s = 0; s < 6; s++) {
            const x = startX + s * stringSpacing;
            const strokeW = 1 + (5 - s) * 0.25; // cordas graves mais espessas
            svg += `<line x1="${x}" y1="${topY}" x2="${x}" y2="${topY + numFrets * fretSpacing}" stroke="#94a3b8" stroke-width="${strokeW}" />`;
        }

        // Barra de Pestana (se aplicável)
        if (barre && barre >= baseFret && barre < baseFret + numFrets) {
            let firstStr = -1, lastStr = -1;
            for (let s = 0; s < 6; s++) {
                if (frets[s] === barre) {
                    if (firstStr === -1) firstStr = s;
                    lastStr = s;
                }
            }
            if (firstStr !== -1 && lastStr > firstStr) {
                const x1 = startX + firstStr * stringSpacing;
                const x2 = startX + lastStr * stringSpacing;
                const y = topY + (barre - baseFret + 0.5) * fretSpacing;
                svg += `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="#38bdf8" stroke-width="12" stroke-linecap="round" opacity="0.85" />`;
            }
        }

        // Bolinhas de dedos e marcadores de corda solta/abafada
        for (let s = 0; s < 6; s++) {
            const f = frets[s];
            const x = startX + s * stringSpacing;

            if (f === -1) {
                // Corda abafada (X)
                svg += `<text x="${x}" y="${topY - 12}" fill="#f43f5e" font-size="11" font-family="sans-serif" font-weight="bold" text-anchor="middle">X</text>`;
            } else if (f === 0) {
                // Corda solta (O)
                svg += `<circle cx="${x}" cy="${topY - 14}" r="4" fill="none" stroke="#34d399" stroke-width="1.8" />`;
            } else if (f >= baseFret && f < baseFret + numFrets) {
                // Dedo pressionado
                const y = topY + (f - baseFret + 0.5) * fretSpacing;
                const isRoot = (s === 0 || s === 1) && f === frets.find(val => val > 0);
                const fillColor = isRoot ? '#38bdf8' : '#f8fafc';

                svg += `<circle cx="${x}" cy="${y}" r="7.5" fill="${fillColor}" stroke="#0284c7" stroke-width="1.5" />`;
            }
        }

        svg += `</svg>`;
        return svg;
    }

    return {
        renderGuitarFretboardSVG: renderGuitarFretboardSVG,
        CHORD_SHAPES: CHORD_SHAPES
    };
});
