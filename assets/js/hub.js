// Lógica dinâmica para o Hub (index.html) - Agrupamentos, Filtros e Ordenação de Cifras
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("song-list-container");
    const searchInput = document.getElementById("search-input");
    const groupSelect = document.getElementById("group-select");
    const sortSelect = document.getElementById("sort-select");
    const quickButtons = document.querySelectorAll(".quick-filter-btn");
    const totalCountEl = document.getElementById("total-count-badge");

    if (typeof SONGS_CATALOG === "undefined") {
        console.warn("SONGS_CATALOG não foi carregado. Operando no modo estático.");
        return;
    }

    let state = {
        search: "",
        group: "none",
        sort: "title-asc",
        quick: "all"
    };

    // Helper para remover acentos na busca/ordenação
    const removeAccents = (str) => {
        return (str || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    };

    // Determinar classe do badge e rótulo de nível
    const getLevelInfo = (count) => {
        if (count <= 5) return { class: "beginner", label: "Iniciante (1 a 5 acordes)", order: 1, icon: "🟢" };
        if (count <= 10) return { class: "intermediate", label: "Intermediário (6 a 10 acordes)", order: 2, icon: "🟡" };
        if (count <= 15) return { class: "advanced", label: "Avançado (11 a 15 acordes)", order: 3, icon: "🟠" };
        return { class: "expert", label: "Expert (16+ acordes)", order: 4, icon: "🔴" };
    };

    // Atualizar contadores nos botões de filtro rápido
    const updateQuickFilterCounts = () => {
        const counts = { all: SONGS_CATALOG.length, beginner: 0, intermediate: 0, advanced: 0, expert: 0 };
        SONGS_CATALOG.forEach(s => {
            if (s.chordsCount <= 5) counts.beginner++;
            else if (s.chordsCount <= 10) counts.intermediate++;
            else if (s.chordsCount <= 15) counts.advanced++;
            else counts.expert++;
        });

        quickButtons.forEach(btn => {
            const filter = btn.dataset.filter;
            const countSpan = btn.querySelector(".btn-count");
            if (countSpan && counts[filter] !== undefined) {
                countSpan.textContent = `(${counts[filter]})`;
            }
        });
        if (totalCountEl) totalCountEl.textContent = `${SONGS_CATALOG.length} músicas disponíveis`;
    };

    // Filtrar músicas
    const getFilteredSongs = () => {
        const query = removeAccents(state.search.trim()).toLowerCase();
        
        return SONGS_CATALOG.filter(song => {
            // Filtro rápido por nível
            if (state.quick === "beginner" && song.chordsCount > 5) return false;
            if (state.quick === "intermediate" && (song.chordsCount < 6 || song.chordsCount > 10)) return false;
            if (state.quick === "advanced" && (song.chordsCount < 11 || song.chordsCount > 15)) return false;
            if (state.quick === "expert" && song.chordsCount < 16) return false;

            // Busca por texto
            if (!query) return true;
            const titleNorm = removeAccents(song.title).toLowerCase();
            const artistNorm = removeAccents(song.artist).toLowerCase();
            const compNorm = removeAccents(song.composer).toLowerCase();
            const idNorm = removeAccents(song.id).toLowerCase();
            return titleNorm.includes(query) || artistNorm.includes(query) || compNorm.includes(query) || idNorm.includes(query);
        });
    };

    // Ordenar músicas
    const sortSongs = (songsList) => {
        return [...songsList].sort((a, b) => {
            const titleA = removeAccents(a.title).toLowerCase();
            const titleB = removeAccents(b.title).toLowerCase();

            if (state.sort === "title-asc") return titleA.localeCompare(titleB);
            if (state.sort === "title-desc") return titleB.localeCompare(titleA);
            if (state.sort === "chords-asc") return (a.chordsCount - b.chordsCount) || titleA.localeCompare(titleB);
            if (state.sort === "chords-desc") return (b.chordsCount - a.chordsCount) || titleA.localeCompare(titleB);
            if (state.sort === "artist-asc") {
                const artA = removeAccents(a.artist).toLowerCase();
                const artB = removeAccents(b.artist).toLowerCase();
                return artA.localeCompare(artB) || titleA.localeCompare(titleB);
            }
            return 0;
        });
    };

    // Renderizar um card individual
    const renderCard = (song) => {
        const level = getLevelInfo(song.chordsCount);
        let artistDisplay = song.artist || "Desconhecido";
        if (song.composer && song.composer !== song.artist) {
            artistDisplay += ` <span class="song-composer">(Comp: ${song.composer})</span>`;
        }

        return `
            <a href="viewer.html?song=${song.id}" class="song-link" data-chords="${song.chordsCount}">
                <div class="song-info">
                    <span class="song-title">${song.title}</span>
                    <span class="song-artist">${artistDisplay}</span>
                </div>
                <div class="song-badges">
                    <span class="chord-badge badge-${level.class}">
                        🎸 ${song.chordsCount} ${song.chordsCount === 1 ? 'acorde' : 'acordes'}
                    </span>
                </div>
            </a>
        `;
    };

    // Renderizar a interface de lista ou grupos
    const render = () => {
        const filtered = getFilteredSongs();
        const sorted = sortSongs(filtered);

        if (sorted.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📂</div>
                    <h3>Nenhuma música encontrada</h3>
                    <p>Tente ajustar os termos da busca ou mudar os filtros selecionados.</p>
                </div>
            `;
            return;
        }

        if (state.group === "none") {
            container.innerHTML = sorted.map(renderCard).join("\n");
            return;
        }

        // Mapeamento de grupos
        const groups = new Map();

        if (state.group === "chords-range") {
            // Pre-iniciar ordem dos níveis
            [1, 2, 3, 4].forEach(order => {
                const sampleCount = order === 1 ? 3 : order === 2 ? 8 : order === 3 ? 12 : 18;
                const info = getLevelInfo(sampleCount);
                groups.set(info.label, { icon: info.icon, order: info.order, songs: [] });
            });
            sorted.forEach(song => {
                const info = getLevelInfo(song.chordsCount);
                if (groups.has(info.label)) {
                    groups.get(info.label).songs.push(song);
                }
            });
        } else if (state.group === "artist") {
            sorted.forEach(song => {
                const artistName = song.artist || "Desconhecido";
                if (!groups.has(artistName)) {
                    groups.set(artistName, { icon: "👤", order: removeAccents(artistName).toLowerCase(), songs: [] });
                }
                groups.get(artistName).songs.push(song);
            });
        } else if (state.group === "letter") {
            sorted.forEach(song => {
                const firstChar = removeAccents(song.title).charAt(0).toUpperCase() || "#";
                const letter = /[A-Z]/.test(firstChar) ? firstChar : "#";
                if (!groups.has(letter)) {
                    groups.set(letter, { icon: "🔠", order: letter, songs: [] });
                }
                groups.get(letter).songs.push(song);
            });
        }

        // Ordenar chaves do grupo
        const sortedKeys = Array.from(groups.keys()).sort((a, b) => {
            const gA = groups.get(a);
            const gB = groups.get(b);
            if (typeof gA.order === "number" && typeof gB.order === "number") {
                return gA.order - gB.order;
            }
            return String(gA.order).localeCompare(String(gB.order));
        });

        // Montar HTML dos grupos
        let html = "";
        sortedKeys.forEach(key => {
            const groupObj = groups.get(key);
            if (groupObj.songs.length === 0) return;

            html += `
                <div class="group-section">
                    <div class="group-header">
                        <span class="group-icon">${groupObj.icon}</span>
                        <span class="group-title">${key}</span>
                        <span class="group-count">${groupObj.songs.length} ${groupObj.songs.length === 1 ? 'música' : 'músicas'}</span>
                    </div>
                    <div class="group-cards">
                        ${groupObj.songs.map(renderCard).join("\n")}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    };

    // Event Listeners
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            state.search = e.target.value;
            render();
        });
    }

    if (groupSelect) {
        groupSelect.addEventListener("change", (e) => {
            state.group = e.target.value;
            render();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener("change", (e) => {
            state.sort = e.target.value;
            render();
        });
    }

    quickButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            quickButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.quick = btn.dataset.filter;
            render();
        });
    });

    // Render inicial
    updateQuickFilterCounts();
    render();
});
