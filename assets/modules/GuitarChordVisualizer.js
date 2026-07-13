/**
 * ============================================================================
 * GuitarChordVisualizer Module (assets/modules/GuitarChordVisualizer.js)
 * ============================================================================
 * Módulo front-end robusto para renderização visual de acordes no braço do
 * violão (fretboard) em SVG, com biblioteca integrada de shapes (posições)
 * e coloração inteligente por função harmônica (Tônica, Tríade, Extensão).
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

    // Dicionário front-end de shapes populares de violão (ordem das cordas: E6, A5, D4, G3, B2, E1)
    // -1 = X (corda abafada), 0 = corda solta, 1..12 = casa
    const CHORD_SHAPES = {
        // Maiores
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

        // Menores
        'Cm': { frets: [-1, 3, 5, 5, 4, 3], baseFret: 3, barre: 3 },
        'Dm': { frets: [-1, -1, 0, 2, 3, 1], baseFret: 1 },
        'Em': { frets: [0, 2, 2, 0, 0, 0], baseFret: 1 },
        'Fm': { frets: [1, 3, 3, 1, 1, 1], baseFret: 1, barre: 1 },
        'Gm': { frets: [3, 5, 5, 3, 3, 3], baseFret: 3, barre: 3 },
        'Am': { frets: [-1, 0, 2, 2, 1, 0], baseFret: 1 },
        'Bm': { frets: [-1, 2, 4, 4, 3, 2], baseFret: 2, barre: 2 },
        'C#m': { frets: [-1, 4, 6, 6, 5, 4], baseFret: 4, barre: 4 },
        'F#m': { frets: [2, 4, 4, 2, 2, 2], baseFret: 2, barre: 2 },
        'G#m': { frets: [4, 6, 6, 4, 4, 4], baseFret: 4, barre: 4 },
        'Bbm': { frets: [-1, 1, 3, 3, 2, 1], baseFret: 1, barre: 1 },

        // Sétimas dominantes (7)
        'C7': { frets: [-1, 3, 2, 3, 1, 0], baseFret: 1 },
        'D7': { frets: [-1, -1, 0, 2, 1, 2], baseFret: 1 },
        'E7': { frets: [0, 2, 0, 1, 0, 0], baseFret: 1 },
        'F7': { frets: [1, 3, 1, 2, 1, 1], baseFret: 1, barre: 1 },
        'G7': { frets: [3, 2, 0, 0, 0, 1], baseFret: 1 },
        'A7': { frets: [-1, 0, 2, 0, 2, 0], baseFret: 1 },
        'B7': { frets: [-1, 2, 1, 2, 0, 2], baseFret: 1 },

        // Sétimas maiores (7M / maj7)
        'C7M': { frets: [-1, 3, 2, 0, 0, 0], baseFret: 1 },
        'D7M': { frets: [-1, -1, 0, 2, 2, 2], baseFret: 1 },
        'E7M': { frets: [0, 2, 1, 1, 0, 0], baseFret: 1 },
        'F7M': { frets: [-1, -1, 3, 2, 1, 0], baseFret: 1 },
        'G7M': { frets: [3, 2, 0, 0, 0, 2], baseFret: 1 },
        'A7M': { frets: [-1, 0, 2, 1, 2, 0], baseFret: 1 },
        'B7M': { frets: [-1, 2, 4, 3, 4, 2], baseFret: 2, barre: 2 },

        // Menores com sétima (m7)
        'Cm7': { frets: [-1, 3, 5, 3, 4, 3], baseFret: 3, barre: 3 },
        'Dm7': { frets: [-1, -1, 0, 2, 1, 1], baseFret: 1 },
        'Em7': { frets: [0, 2, 2, 0, 3, 0], baseFret: 1 },
        'Fm7': { frets: [1, 3, 1, 1, 1, 1], baseFret: 1, barre: 1 },
        'Gm7': { frets: [3, 5, 3, 3, 3, 3], baseFret: 3, barre: 3 },
        'Am7': { frets: [-1, 0, 2, 0, 1, 0], baseFret: 1 },
        'Bm7': { frets: [-1, 2, 4, 2, 3, 2], baseFret: 2, barre: 2 },
        'C#m7': { frets: [-1, 4, 6, 4, 5, 4], baseFret: 4, barre: 4 },
        'F#m7': { frets: [2, 4, 2, 2, 2, 2], baseFret: 2, barre: 2 },

        // Acordes com Baixo Invertido / Especiais
        'D7/F#': { frets: [2, 0, 0, 2, 1, 2], baseFret: 1 },
        'G/F': { frets: [1, 2, 0, 0, 0, 3], baseFret: 1 },
        'F/A': { frets: [-1, 0, 3, 2, 1, 1], baseFret: 1 },
        'G/B': { frets: [-1, 2, 0, 0, 0, 3], baseFret: 1 },
        'C/E': { frets: [0, 3, 2, 0, 1, 0], baseFret: 1 },

        // Acordes de Bossa / Samba / MPB
        'C7(9)': { frets: [-1, 3, 2, 3, 3, -1], baseFret: 1 },
        'D7(9)': { frets: [-1, 5, 4, 5, 5, -1], baseFret: 4 },
        'E7(9)': { frets: [0, 7, 6, 7, 7, -1], baseFret: 5 },
        'A7(9)': { frets: [-1, 0, 5, 6, 5, -1], baseFret: 4 },
        'C#m7(5-)': { frets: [-1, 4, 5, 4, 5, -1], baseFret: 3 },
        'F#m7(5-)': { frets: [2, -1, 2, 2, 1, -1], baseFret: 1 },
        'Bm7(5-)': { frets: [-1, 2, 3, 2, 3, -1], baseFret: 1 },
        'C7(4/9)': { frets: [-1, 3, 3, 3, 3, -1], baseFret: 1 }
    };

    /**
     * Resolve o shape do acorde pelo nome com fallback inteligente.
     */
    function resolveChordShape(chordName) {
        if (!chordName) return null;
        const cleanName = chordName.trim();
        if (CHORD_SHAPES[cleanName]) {
            return CHORD_SHAPES[cleanName];
        }
        // Tenta remover extensões se não achar exato (ex: C6(9) -> C6 ou C)
        const baseRootMatch = cleanName.match(/^[A-G][b#]?m?7?M?/);
        if (baseRootMatch && CHORD_SHAPES[baseRootMatch[0]]) {
            return CHORD_SHAPES[baseRootMatch[0]];
        }
        const rootOnly = cleanName.match(/^[A-G][b#]?m?/);
        if (rootOnly && CHORD_SHAPES[rootOnly[0]]) {
            return CHORD_SHAPES[rootOnly[0]];
        }
        // Fallback genérico se não encontrado
        return { frets: [-1, 3, 2, 0, 1, 0], baseFret: 1 };
    }

    /**
     * Renderiza o SVG do braço do violão com as casas, cordas e bolinhas.
     */
    function renderGuitarFretboardSVG(chordName) {
        const shape = resolveChordShape(chordName);
        if (!shape) return '';

        const frets = shape.frets;
        const baseFret = shape.baseFret || 1;

        const width = 190;
        const height = 175;
        const leftPad = 32;
        const rightPad = 15;
        const topPad = 35;
        const stringSpacing = (width - leftPad - rightPad) / 5;
        const fretSpacing = 25;
        const numFrets = 5;

        let svg = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" style="max-width: 200px; display: block; margin: 0 auto;">`;

        // Indicador de casa inicial no lado esquerdo se baseFret > 1
        if (baseFret > 1) {
            svg += `<text x="8" y="${topPad + 16}" fill="#94a3b8" font-size="11" font-weight="700" font-family="'Outfit', sans-serif">${baseFret}ª</text>`;
        }

        // Desenhar Nut (pestana superior) ou linha fina da primeira casa
        if (baseFret === 1) {
            svg += `<line x1="${leftPad}" y1="${topPad}" x2="${width - rightPad}" y2="${topPad}" stroke="#e2e8f0" stroke-width="4" stroke-linecap="round"/>`;
        } else {
            svg += `<line x1="${leftPad}" y1="${topPad}" x2="${width - rightPad}" y2="${topPad}" stroke="#64748b" stroke-width="1.5"/>`;
        }

        // Desenhar trastes horizontais
        for (let i = 1; i <= numFrets; i++) {
            const y = topPad + i * fretSpacing;
            svg += `<line x1="${leftPad}" y1="${y}" x2="${width - rightPad}" y2="${y}" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>`;
        }

        // Desenhar cordas verticais (6 cordas)
        for (let s = 0; s < 6; s++) {
            const x = leftPad + s * stringSpacing;
            svg += `<line x1="${x}" y1="${topPad}" x2="${x}" y2="${topPad + numFrets * fretSpacing}" stroke="rgba(255,255,255,0.45)" stroke-width="${1 + (5 - s) * 0.25}"/>`;
        }

        // Pestana (Barre)
        if (shape.barre && shape.barre >= baseFret) {
            const relFret = shape.barre - baseFret + 1;
            const y = topPad + (relFret - 0.5) * fretSpacing;
            svg += `<rect x="${leftPad}" y="${y - 6}" width="${width - leftPad - rightPad}" height="12" rx="6" fill="rgba(52, 211, 153, 0.35)"/>`;
        }

        // Desenhar marcações de corda solta (O), abafada (X) e bolinhas
        for (let s = 0; s < 6; s++) {
            const fretVal = frets[s];
            const x = leftPad + s * stringSpacing;

            if (fretVal === -1 || fretVal === 'X') {
                // Corda abafada
                svg += `<text x="${x}" y="${topPad - 12}" fill="#ef4444" font-size="12" font-weight="700" text-anchor="middle" font-family="'Outfit', sans-serif">✕</text>`;
            } else if (fretVal === 0) {
                // Corda solta
                svg += `<circle cx="${x}" cy="${topPad - 15}" r="4" fill="none" stroke="#38bdf8" stroke-width="1.8"/>`;
            } else {
                // Bolinha pressionada
                const relFret = fretVal - baseFret + 1;
                if (relFret >= 1 && relFret <= numFrets) {
                    const y = topPad + (relFret - 0.5) * fretSpacing;
                    // Tônica na corda mais grave pressionada (Verde #34d399), restante em Ciano #38bdf8
                    let color = s === 0 || (s === 1 && frets[0] === -1) ? '#34d399' : '#38bdf8';
                    svg += `<circle cx="${x}" cy="${y}" r="8" fill="${color}" stroke="#0f172a" stroke-width="1.5"/>`;
                }
            }
        }

        svg += `</svg>`;
        return svg;
    }

    return {
        CHORD_SHAPES,
        resolveChordShape,
        renderGuitarFretboardSVG
    };
});
