document.addEventListener("scroll", function (): void {
    const header = document.getElementById("main-header");
    if (!header) return;

    if (window.scrollY > 10) {
        header.classList.add("bg-white", "backdrop-blur-md", "border-b");
        header.classList.remove("bg-transparent");
    } else {
        header.classList.remove("bg-white", "backdrop-blur-md", "border-b");
        header.classList.add("bg-transparent");
    }
});
