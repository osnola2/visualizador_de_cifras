/**
 * ChordSynth.js - Sintetizador nativo via Web Audio API com sonoridade realista de instrumento
 * Corrige prioridade de notas para respeitar alturas exatas (ex: C3, E4) e adiciona filtro/reverb harmônico.
 * Possui proteção anti-saturação com limiter brickwall, voice stealing (corte suave de acordes anteriores) e throttle no scroll.
 */
class ChordSynth {
    constructor() {
        this.ctx = null;
        this.isAudioEnabled = false;
        this.currentTimbre = 'acoustic'; // 'acoustic', 'piano', 'pad'
        this.masterGain = null;
        this.limiter = null;
        this.reverbNode = null;
        this.activeVoices = [];
        this.lastChordTime = 0;
        this.NOTE_MAP = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
            'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
            'A#': 10, 'Bb': 10, 'B': 11
        };
    }

    init() {
        if (!this.ctx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                this.ctx = new AudioContextClass();
                this.setupMasterBus();
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    setupMasterBus() {
        if (!this.ctx) return;
        
        // 1. Limiter Brickwall (DynamicsCompressorNode) para impedir que o áudio estoure ou distorça (> 0dBFS) no scroll rápido
        this.limiter = this.ctx.createDynamicsCompressor();
        this.limiter.threshold.setValueAtTime(-4.0, this.ctx.currentTime); // Segura picos a partir de -4 dB
        this.limiter.knee.setValueAtTime(0.0, this.ctx.currentTime);       // Hard knee para corte limpo
        this.limiter.ratio.setValueAtTime(20.0, this.ctx.currentTime);     // Ratio 20:1 (limiter robusto)
        this.limiter.attack.setValueAtTime(0.001, this.ctx.currentTime);   // Ataque instantâneo (1ms)
        this.limiter.release.setValueAtTime(0.12, this.ctx.currentTime);   // Liberação rápida (120ms)
        this.limiter.connect(this.ctx.destination);

        // 2. Master Gain conectando no Limiter
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.setValueAtTime(0.68, this.ctx.currentTime); // Headroom seguro
        this.masterGain.connect(this.limiter);

        // 3. Reverb sintético (ConvolverNode) para acústica de sala de violão/piano
        try {
            const length = this.ctx.sampleRate * 1.8; // 1.8s cauda de reverb
            const impulse = this.ctx.createBuffer(2, length, this.ctx.sampleRate);
            for (let channel = 0; channel < 2; channel++) {
                const channelData = impulse.getChannelData(channel);
                for (let i = 0; i < length; i++) {
                    channelData[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 3.5);
                }
            }
            this.reverbNode = this.ctx.createConvolver();
            this.reverbNode.buffer = impulse;

            const reverbGain = this.ctx.createGain();
            reverbGain.gain.setValueAtTime(0.20, this.ctx.currentTime); // 20% wet
            this.reverbNode.connect(reverbGain);
            reverbGain.connect(this.masterGain);
        } catch (e) {
            console.warn("Reverb falhou, operando com som direto:", e);
        }
    }

    toggleAudio() {
        this.isAudioEnabled = !this.isAudioEnabled;
        if (this.isAudioEnabled) {
            this.init();
        } else {
            this.stopActiveVoices(0.02);
        }
        return this.isAudioEnabled;
    }

    setTimbre(timbre) {
        this.currentTimbre = timbre;
    }

    noteToFreq(noteStr, index = 0) {
        if (typeof noteStr === 'number') {
            return 440 * Math.pow(2, (noteStr - 69) / 12);
        }
        if (!noteStr || typeof noteStr !== 'string') return 440;

        const match = noteStr.match(/^([A-Ga-g][#b]?)(-?\d+)?$/);
        if (!match) return 440;

        const name = match[1].toUpperCase();
        const octave = match[2] !== undefined ? parseInt(match[2], 10) : (index === 0 ? 3 : 4);
        const semitone = this.NOTE_MAP[name];
        if (semitone === undefined) return 440;

        const midi = (octave + 1) * 12 + semitone;
        return 440 * Math.pow(2, (midi - 69) / 12);
    }

    /**
     * Limpa e suaviza notas anteriores (Voice Stealing) para evitar acúmulo e estresse sonoro
     */
    stopActiveVoices(fadeDuration = 0.06) {
        if (!this.ctx || !this.activeVoices || this.activeVoices.length === 0) return;
        const now = this.ctx.currentTime;
        
        this.activeVoices.forEach(v => {
            try {
                if (v.stopTime > now) {
                    v.gain.gain.cancelScheduledValues(now);
                    v.gain.gain.setValueAtTime(v.gain.gain.value || 0.05, now);
                    v.gain.gain.exponentialRampToValueAtTime(0.0001, now + fadeDuration);
                    v.osc1.stop(now + fadeDuration + 0.01);
                    v.osc2.stop(now + fadeDuration + 0.01);
                }
            } catch (e) {
                // Voz já expirada ou parada
            }
        });
        this.activeVoices = [];
    }

    /**
     * Toca uma voz harmônica com 2 osciladores e filtro de corpo acústico
     */
    playVoice(freq, startTime, duration = 2.2, gainLevel = 0.18, isBass = false) {
        if (!this.ctx || !this.masterGain) return;

        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const filter = this.ctx.createBiquadFilter();
        const voiceGain = this.ctx.createGain();

        if (this.currentTimbre === 'piano') {
            osc1.type = 'triangle';
            osc2.type = 'sine';
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(2800, startTime);
            filter.frequency.exponentialRampToValueAtTime(450, startTime + duration);
            osc1.frequency.setValueAtTime(freq, startTime);
            osc2.frequency.setValueAtTime(freq * 2.001, startTime);
        } else if (this.currentTimbre === 'pad') {
            osc1.type = 'sawtooth';
            osc2.type = 'triangle';
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(600, startTime);
            filter.frequency.linearRampToValueAtTime(1600, startTime + duration * 0.5);
            osc1.frequency.setValueAtTime(freq, startTime);
            osc2.frequency.setValueAtTime(freq * 1.003, startTime);
        } else {
            // 'acoustic' - Violão / Cavaquinho
            osc1.type = 'triangle';
            osc2.type = 'sawtooth';
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(isBass ? 1800 : 3400, startTime);
            filter.frequency.exponentialRampToValueAtTime(isBass ? 300 : 450, startTime + duration * 0.8);
            
            osc1.frequency.setValueAtTime(freq, startTime);
            osc2.frequency.setValueAtTime(freq * 1.0018, startTime);
        }

        osc1.connect(filter);
        osc2.connect(filter);
        filter.connect(voiceGain);
        
        voiceGain.connect(this.masterGain);
        if (this.reverbNode) {
            voiceGain.connect(this.reverbNode);
        }

        voiceGain.gain.setValueAtTime(0.0001, startTime);
        voiceGain.gain.linearRampToValueAtTime(gainLevel, startTime + 0.015);
        voiceGain.gain.exponentialRampToValueAtTime(gainLevel * 0.45, startTime + 0.3);
        voiceGain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

        osc1.start(startTime);
        osc2.start(startTime);
        osc1.stop(startTime + duration + 0.1);
        osc2.stop(startTime + duration + 0.1);

        this.activeVoices.push({ osc1, osc2, gain: voiceGain, stopTime: startTime + duration + 0.1 });
    }

    /**
     * Toca um conjunto de notas em dedilhado acústico arpejado
     */
    playChordNotes(notes, options = {}) {
        if (!this.isAudioEnabled) return;
        this.init();
        if (!this.ctx || this.ctx.state !== 'running') return;

        let noteList = [];
        if (Array.isArray(notes)) {
            noteList = notes;
        } else if (notes && typeof notes === 'object') {
            noteList = notes.notes || notes.displayNotes || [];
        }

        if (!noteList || noteList.length === 0) return;

        const now = this.ctx.currentTime;
        const duration = options.duration || 2.4;
        const strumSpeed = options.strumSpeed !== undefined ? options.strumSpeed : 0.038;
        
        const baseGain = Math.min(0.22, 0.48 / Math.sqrt(noteList.length));

        const voicedNotes = noteList.map((noteStr, idx) => ({
            noteStr,
            freq: this.noteToFreq(noteStr, idx),
            originalIndex: idx
        })).sort((a, b) => a.freq - b.freq);

        voicedNotes.forEach((item, index) => {
            const startTime = now + (options.arpeggiate === false ? 0 : index * strumSpeed);
            const isBass = index === 0;
            this.playVoice(item.freq, startTime, duration, isBass ? baseGain * 1.15 : baseGain, isBass);
        });
    }

    /**
     * Acionado ao clicar ou avançar no Auto-scroll para tocar um acorde.
     * Inclui controle anti-rajada (throttle) e voice stealing.
     */
    triggerChord(chordDataObj) {
        if (!this.isAudioEnabled || !chordDataObj) return;
        this.init();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        // Throttle: se o scroll for extremamente rápido (< 85ms entre acordes), ignora para não virar metralhadora
        if (this.lastChordTime && (now - this.lastChordTime < 0.085)) {
            return;
        }
        this.lastChordTime = now;

        // Voice Stealing: suaviza e corta as vozes do acorde anterior em 60ms para evitar sobreposição infinita
        this.stopActiveVoices(0.06);

        this.playChordNotes(chordDataObj);
    }
}

// Instância global para ser usada em todos os visualizadores
window.chordSynth = new ChordSynth();
