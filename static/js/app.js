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
});
