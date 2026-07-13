import re

NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

def get_note_index(note_str):
    if note_str in NOTES_SHARP: return NOTES_SHARP.index(note_str)
    if note_str in NOTES_FLAT: return NOTES_FLAT.index(note_str)
    # Edge cases
    if note_str == 'Cb': return 11
    if note_str == 'E#': return 5
    if note_str == 'Fb': return 4
    if note_str == 'B#': return 0
    return 0

def get_note_name(index, use_flats=False):
    idx = index % 12
    return NOTES_FLAT[idx] if use_flats else NOTES_SHARP[idx]

def parse_chord(chord_symbol):
    """
    Parses a chord symbol and returns:
    (notes_with_octave, display_notes, note_types)
    """
    # 1. Extract Bass if present
    bass = None
    bass_match = re.search(r'/([A-G][#b]?)$', chord_symbol)
    if bass_match:
        bass = bass_match.group(1)
        chord_symbol = chord_symbol[:bass_match.start()]

    # 2. Extract Root
    root_match = re.match(r'^([A-G][#b]?)', chord_symbol)
    if not root_match:
        return (['C3', 'E3', 'G3'], ['C', 'E', 'G'], ['root', 'triad', 'triad']) # Fallback
    
    root_str = root_match.group(1)
    root_idx = get_note_index(root_str)
    use_flats = 'b' in root_str or root_str == 'F'

    suffix = chord_symbol[len(root_str):]
    
    # 3. Base Intervals (Root, Third, Fifth)
    intervals = {0: 'root'}
    
    # Analyze Quality
    is_minor = False
    is_dim = False
    is_aug = False
    is_sus4 = False
    is_sus2 = False
    
    # Extract qualities
    if re.search(r'm(?!aj)', suffix) or '-' in suffix:
        is_minor = True
    if 'dim' in suffix or 'º' in suffix or '°' in suffix:
        is_dim = True
        is_minor = True
    if 'aug' in suffix or '+' in suffix and '11+' not in suffix and '9+' not in suffix:
        is_aug = True
    if 'sus4' in suffix or ('sus' in suffix and 'sus2' not in suffix):
        is_sus4 = True
    if 'sus2' in suffix:
        is_sus2 = True

    # Thirds
    if is_sus4:
        intervals[5] = 'triad' # Perf 4th
    elif is_sus2:
        intervals[2] = 'triad' # Maj 2nd
    elif is_minor:
        intervals[3] = 'triad' # Min 3rd
    else:
        intervals[4] = 'triad' # Maj 3rd
        
    # Fifths
    if is_dim or 'b5' in suffix:
        intervals[6] = 'triad' # Dim 5th
    elif is_aug or '#5' in suffix or '5+' in suffix:
        intervals[8] = 'triad' # Aug 5th
    else:
        intervals[7] = 'triad' # Perf 5th

    # 4. Analyze Sevenths & Extensions
    # Sevenths and Sixths
    if 'maj7' in suffix or 'M7' in suffix or '7M' in suffix:
        intervals[11] = 'seventh'
    elif '6' in suffix:
        intervals[9] = 'seventh' # Treat 6th as the 7th block for coloring
    elif '7' in suffix or '9' in suffix or '11' in suffix or '13' in suffix:
        # If it's diminished 7th
        if 'dim7' in suffix or 'º7' in suffix or '°7' in suffix:
            intervals[9] = 'seventh' # Diminished 7th (enharmonic to maj 6)
        else:
            if 'add9' not in suffix and 'add11' not in suffix:
                intervals[10] = 'seventh' # Minor 7th (dominant)
            
    # Ninths
    if '9' in suffix or '2' in suffix:
        if 'maj9' in suffix:
            intervals[11] = 'seventh'
            intervals[14] = 'ninth' # maj9
        elif 'b9' in suffix or '9-' in suffix:
            intervals[13] = 'alt' # min9
        elif '#9' in suffix or '9+' in suffix:
            intervals[15] = 'alt' # aug9
        else:
            intervals[14] = 'ninth' # maj9
            
    # Add chords (if not handled above)
    if 'add9' in suffix or 'add2' in suffix:
        intervals[14] = 'ninth'
    if 'add11' in suffix or 'add4' in suffix:
        intervals[17] = 'alt'
        
    # Elevenths and Thirteenths
    if '11' in suffix:
        intervals[14] = 'ninth' # implicit 9
        if '#11' in suffix or '11+' in suffix:
            intervals[18] = 'alt'
        else:
            intervals[17] = 'alt'
    
    if '13' in suffix:
        intervals[14] = 'ninth' # implicit 9
        if 'b13' in suffix or '13-' in suffix:
            intervals[20] = 'alt'
        else:
            intervals[21] = 'alt'
            
    # Other Alterations fallback
    if 'b5' in suffix and 6 not in intervals:
        if 7 in intervals: del intervals[7]
        intervals[6] = 'triad'
    if ('#5' in suffix or '5+' in suffix) and 8 not in intervals:
        if 7 in intervals: del intervals[7]
        intervals[8] = 'triad'

    # 5. Bass note processing
    if bass:
        bass_idx = get_note_index(bass)
        bass_diff = (bass_idx - root_idx) % 12
        if bass_diff < 0:
            bass_diff += 12
        
        # Add it as a lower bass note (one octave below the root)
        intervals[-12 + bass_diff] = 'bass'
        
    # 6. Build the final arrays
    sorted_intervals = sorted(list(intervals.keys()))
    
    # Ensure the lowest note is at least C3 (absolute 0)
    # so it renders on the 2-octave piano visualizer.
    min_absolute_semitone = root_idx + sorted_intervals[0]
    octave_shift = 1 if min_absolute_semitone < 0 else 0
    
    notes_with_octave = []
    display_notes = []
    note_types = []
    
    base_octave = 3 + octave_shift
    
    for interval in sorted_intervals:
        absolute_semitones = root_idx + interval
        
        # Calculate true octave taking negative intervals into account
        octave = base_octave + (absolute_semitones // 12)
        note_name_display = get_note_name(absolute_semitones, use_flats)
        note_name_dom = get_note_name(absolute_semitones, False)
        
        notes_with_octave.append(f"{note_name_dom}{octave}")
        display_notes.append(note_name_display)
        note_types.append(intervals[interval])
        
    return notes_with_octave, display_notes, note_types

if __name__ == "__main__":
    # Test cases
    test_chords = ["C", "Cm", "Cmaj7", "Cm7", "Cdim", "Caug", "C7", "C9", "C13", "F#m7(b5)", "G7(b9)", "A/C#"]
    for c in test_chords:
        print(f"{c}: {parse_chord(c)}")
