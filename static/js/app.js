document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll("[data-clickable-row]");
    let draggedCard = null;
    let dragOriginCell = null;
    const boardSnapshots = new Map();

    const getCleanScheduleHtml = (scheduleGrid) => {
        const clone = scheduleGrid.cloneNode(true);
        clone.querySelectorAll("[data-drag-bound], [data-drop-bound]").forEach((element) => {
            delete element.dataset.dragBound;
            delete element.dataset.dropBound;
            element.classList.remove("dragging", "drag-over", "drop-rejected");
        });
        return clone.innerHTML;
    };

    rows.forEach((row) => {
        row.addEventListener("click", () => {
            const target = row.getAttribute("data-clickable-row");
            if (target) {
                window.location.href = target;
            }
        });
    });

    const updateFichaCounters = () => {
        document.querySelectorAll(".assignment-card[data-max-hours]").forEach((trayCard) => {
            const fichaId = trayCard.dataset.fichaId;
            const maxHours = Number(trayCard.dataset.maxHours || 0);
            const placed = document.querySelectorAll(`.placed-card[data-ficha-id="${fichaId}"]`).length;
            const remaining = Math.max(maxHours - placed, 0);
            trayCard.dataset.remainingHours = String(remaining);
            trayCard.setAttribute("draggable", remaining > 0 ? "true" : "false");
            trayCard.classList.toggle("is-empty", remaining <= 0);

            const label = trayCard.querySelector("[data-remaining-label]");
            if (label) {
                label.textContent = String(remaining);
            }
        });
        document.dispatchEvent(new CustomEvent("schedule:fichas-updated"));
    };

    const bindCardDrag = (card) => {
        if (card.dataset.dragBound === "true") {
            return;
        }
        card.dataset.dragBound = "true";

        card.addEventListener("dragstart", (event) => {
            if (card.dataset.maxHours && Number(card.dataset.remainingHours || 0) <= 0) {
                event.preventDefault();
                return;
            }
            draggedCard = card;
            dragOriginCell = card.closest(".drop-cell");
            card.classList.add("dragging");
        });

        card.addEventListener("dragend", () => {
            card.classList.remove("dragging");
            draggedCard = null;
            dragOriginCell = null;
        });
    };

    document.querySelectorAll(".assignment-card").forEach(bindCardDrag);

    const createPlacedCard = (sourceCard) => {
        const card = document.createElement("article");
        card.className = "assignment-card placed-card";
        card.draggable = true;
        card.style.setProperty("--card-color", sourceCard.style.getPropertyValue("--card-color") || "#0f766e");
        ["fichaId", "groupId", "groupCode", "grade", "materiaId", "teacher", "materia", "groupLabel", "aula"].forEach((key) => {
            if (sourceCard.dataset[key]) {
                card.dataset[key] = sourceCard.dataset[key];
            }
        });
        card.innerHTML = `
            <strong>${sourceCard.dataset.teacher || ""}</strong>
            <span>${sourceCard.dataset.materia || ""} - ${sourceCard.dataset.groupLabel || ""}</span>
            <small>Aula ${sourceCard.dataset.aula || "pendiente"}</small>
        `;
        bindCardDrag(card);
        return card;
    };

    const bindDropCell = (cell) => {
        if (cell.dataset.dropBound === "true") {
            return;
        }
        cell.dataset.dropBound = "true";

        cell.addEventListener("dragover", (event) => {
            event.preventDefault();
            if (draggedCard && cell.dataset.grupo === draggedCard.dataset.groupId && cell.textContent.trim() !== "RECESO") {
                cell.classList.add("drag-over");
            } else {
                cell.classList.add("drop-rejected");
            }
        });

        cell.addEventListener("dragleave", () => {
            cell.classList.remove("drag-over");
            cell.classList.remove("drop-rejected");
        });

        cell.addEventListener("drop", (event) => {
            event.preventDefault();
            cell.classList.remove("drag-over");
            cell.classList.remove("drop-rejected");

            if (!draggedCard || cell.textContent.trim() === "RECESO" || cell.dataset.grupo !== draggedCard.dataset.groupId) {
                return;
            }

            if (cell.querySelector(".placed-card") && cell !== dragOriginCell) {
                return;
            }

            if (draggedCard.classList.contains("placed-card")) {
                cell.innerHTML = "";
                cell.appendChild(draggedCard);
            } else {
                if (Number(draggedCard.dataset.remainingHours || 0) <= 0) {
                    return;
                }
                const placedCard = createPlacedCard(draggedCard);
                cell.innerHTML = "";
                cell.appendChild(placedCard);
            }
            updateFichaCounters();
        });
    };

    const bindBoardInteractions = (board = document) => {
        board.querySelectorAll(".assignment-card").forEach(bindCardDrag);
        board.querySelectorAll(".drop-cell").forEach(bindDropCell);
    };

    bindBoardInteractions();

    document.querySelectorAll(".assignment-tray").forEach((tray) => {
        tray.addEventListener("dragover", (event) => {
            if (draggedCard && draggedCard.classList.contains("placed-card")) {
                event.preventDefault();
                tray.classList.add("tray-return-active");
            }
        });

        tray.addEventListener("dragleave", () => {
            tray.classList.remove("tray-return-active");
        });

        tray.addEventListener("drop", (event) => {
            if (!draggedCard || !draggedCard.classList.contains("placed-card")) {
                return;
            }
            event.preventDefault();
            tray.classList.remove("tray-return-active");
            draggedCard.remove();
            updateFichaCounters();
        });
    });

    updateFichaCounters();

    const boardFilters = document.querySelector("[data-board-filters]");
    const groupBoards = document.querySelectorAll("[data-group-board]");
    const teacherTrays = document.querySelectorAll(".teacher-tray");
    const scheduleBoard = document.querySelector("[data-schedule-board]");

    if (boardFilters && groupBoards.length) {
        const filterButtons = boardFilters.querySelectorAll("[data-filter-type]");
        const groupFilterButtons = boardFilters.querySelectorAll(".group-filter-chip");
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

        const showTrayCards = ({ grade, groupId, groupCode }) => {
            teacherTrays.forEach((tray) => {
                const cards = tray.querySelectorAll(".assignment-card[data-max-hours]");
                let visibleCount = 0;
                let visibleHours = 0;

                cards.forEach((card) => {
                    const matchesGrade = !grade || card.dataset.grade === grade;
                    const matchesGroup = !groupId || `grupo-${card.dataset.groupId}` === groupId || card.dataset.groupCode === groupCode;
                    const isVisible = matchesGrade && matchesGroup;
                    card.hidden = !isVisible;
                    card.classList.toggle("is-filtered-out", !isVisible);

                    if (isVisible) {
                        visibleCount += 1;
                        visibleHours += Number(card.dataset.remainingHours || 0);
                    }
                });

                tray.hidden = visibleCount === 0;
                tray.open = visibleCount > 0 && Boolean(grade || groupId);

                const pendingLabel = tray.querySelector("[data-teacher-pending]");
                if (pendingLabel) {
                    pendingLabel.textContent = `${visibleHours} h pendientes`;
                }
            });
        };

        const showGroupChips = ({ grade }) => {
            groupFilterButtons.forEach((button) => {
                const isVisible = !grade || button.dataset.grade === grade;
                button.hidden = !isVisible;
                if (!isVisible) {
                    button.classList.remove("active");
                }
            });
        };

        const applyFilter = ({ grade, groupId, groupCode }) => {
            showBoards({ grade, groupId });
            showTrayCards({ grade, groupId, groupCode });
            showGroupChips({ grade });
        };

        const getActiveFilter = () => {
            const activeButton = boardFilters.querySelector("[data-filter-type].active");
            if (!activeButton || activeButton.dataset.filterType === "general") {
                return {};
            }
            if (activeButton.dataset.filterType === "grade") {
                return { grade: activeButton.dataset.grade };
            }
            return { groupId: activeButton.dataset.group, groupCode: activeButton.dataset.groupCode };
        };

        filterButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const type = button.dataset.filterType;
                setActiveFilter(button);

                if (type === "general") {
                    applyFilter({});
                    return;
                }

                if (type === "grade") {
                    applyFilter({ grade: button.dataset.grade });
                    return;
                }

                if (type === "group") {
                    applyFilter({ groupId: button.dataset.group, groupCode: button.dataset.groupCode });
                }
            });
        });

        applyFilter({});
        document.addEventListener("schedule:fichas-updated", () => applyFilter(getActiveFilter()));

        if (filterToggle) {
            filterToggle.addEventListener("click", () => {
                const isCollapsed = boardFilters.classList.toggle("is-collapsed");
                filterToggle.setAttribute("aria-expanded", String(!isCollapsed));
                filterToggle.setAttribute("title", isCollapsed ? "Mostrar filtros" : "Ocultar filtros");
                filterToggle.textContent = isCollapsed ? "v" : "^";
            });
        }
    }

    if (scheduleBoard) {
        document.querySelectorAll("[data-view-mode]").forEach((button) => {
            button.addEventListener("click", () => {
                const isComplete = button.dataset.viewMode === "complete";
                scheduleBoard.classList.toggle("view-complete", isComplete);
                document.querySelectorAll("[data-view-mode]").forEach((modeButton) => {
                    modeButton.classList.toggle("active", modeButton === button);
                });
            });
        });
    }

    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    };

    document.querySelectorAll("[data-save-board]").forEach((button) => {
        button.addEventListener("click", async () => {
            const board = button.closest("[data-group-board]");
            const clases = Array.from(board.querySelectorAll(".drop-cell .placed-card")).map((card) => {
                const cell = card.closest(".drop-cell");
                return {
                    ficha_id: Number(card.dataset.fichaId),
                    dia: cell.dataset.dia,
                    bloque_id: Number(cell.dataset.bloque),
                };
            });

            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = "Guardando...";

            try {
                const response = await fetch(board.dataset.saveUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({ clases }),
                });
                const result = await response.json();
                if (!response.ok || !result.ok) {
                    throw new Error(result.error || "No se pudo guardar.");
                }

                const label = board.querySelector("[data-last-saved]");
                if (label) {
                    label.textContent = result.last_saved;
                }
                const scheduleGrid = board.querySelector(".schedule-grid");
                if (scheduleGrid) {
                    boardSnapshots.set(board.id, getCleanScheduleHtml(scheduleGrid));
                }
                button.textContent = "Guardado";
                updateFichaCounters();
                window.setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1000);
            } catch (error) {
                button.textContent = originalText;
                button.disabled = false;
                alert(error.message);
            }
        });
    });

    document.querySelectorAll("[data-group-board]").forEach((board) => {
        const scheduleGrid = board.querySelector(".schedule-grid");
        if (scheduleGrid) {
            boardSnapshots.set(board.id, getCleanScheduleHtml(scheduleGrid));
        }
    });

    document.querySelectorAll("[data-cancel-board]").forEach((button) => {
        button.addEventListener("click", () => {
            const board = button.closest("[data-group-board]");
            const scheduleGrid = board.querySelector(".schedule-grid");
            const snapshot = boardSnapshots.get(board.id);

            if (!scheduleGrid || snapshot === undefined) {
                return;
            }

            scheduleGrid.innerHTML = snapshot;
            bindBoardInteractions(board);
            updateFichaCounters();
            button.textContent = "Cancelado";
            window.setTimeout(() => {
                button.textContent = "Cancelar";
            }, 900);
        });
    });
});
