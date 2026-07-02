setTimeout((): void => {
    const container = document.getElementById("flash-container");
    if (!container) return;

    container.style.opacity = "0";
    container.style.transform = "translateY(10px)";
    setTimeout((): void => container.remove(), 500);
}, 4000);
