document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll("[data-clickable-row]");
    let draggedCard = null;

    rows.forEach((row) => {
        row.addEventListener("click", () => {
            const target = row.getAttribute("data-clickable-row");
            if (target) {
                window.location.href = target;
            }
        });
    });

    document.querySelectorAll(".assignment-card").forEach((card) => {
        card.addEventListener("dragstart", () => {
            draggedCard = card;
            card.classList.add("dragging");
        });

        card.addEventListener("dragend", () => {
            card.classList.remove("dragging");
            draggedCard = null;
        });
    });

    document.querySelectorAll(".drop-cell").forEach((cell) => {
        cell.addEventListener("dragover", (event) => {
            event.preventDefault();
            cell.classList.add("drag-over");
        });

        cell.addEventListener("dragleave", () => {
            cell.classList.remove("drag-over");
        });

        cell.addEventListener("drop", (event) => {
            event.preventDefault();
            cell.classList.remove("drag-over");

            if (!draggedCard || cell.textContent.trim() === "RECESO") {
                return;
            }

            const clone = draggedCard.cloneNode(true);
            clone.setAttribute("draggable", "false");
            cell.innerHTML = "";
            cell.appendChild(clone);
        });
    });

    const boardFilters = document.querySelector("[data-board-filters]");
    const groupBoards = document.querySelectorAll("[data-group-board]");

    if (boardFilters && groupBoards.length) {
        const filterButtons = boardFilters.querySelectorAll("[data-filter-type]");
        const filterToggle = boardFilters.querySelector("[data-filter-toggle]");

        const setActiveFilter = (activeButton) => {
            filterButtons.forEach((button) => button.classList.remove("active"));
            activeButton.classList.add("active");
        };

        const showBoards = ({ grade, groupId }) => {
            groupBoards.forEach((board) => {
                const matchesGrade = !grade || board.dataset.grade === grade;
                const matchesGroup = !groupId || board.id === groupId;
                board.hidden = !(matchesGrade && matchesGroup);
            });
        };

        filterButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const type = button.dataset.filterType;
                setActiveFilter(button);

                if (type === "general") {
                    showBoards({});
                    return;
                }

                if (type === "grade") {
                    showBoards({ grade: button.dataset.grade });
                    return;
                }

                if (type === "group") {
                    showBoards({ groupId: button.dataset.group });
                }
            });
        });

        if (filterToggle) {
            filterToggle.addEventListener("click", () => {
                const isCollapsed = boardFilters.classList.toggle("is-collapsed");
                filterToggle.setAttribute("aria-expanded", String(!isCollapsed));
                filterToggle.setAttribute("title", isCollapsed ? "Mostrar filtros" : "Ocultar filtros");
                filterToggle.textContent = isCollapsed ? "v" : "^";
            });
        }
    }
});
