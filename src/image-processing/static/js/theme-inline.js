(() => {
    const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("theme="));

    const theme = cookie?.split("=")[1];

    document.documentElement.setAttribute(
        "data-bs-theme",
        theme === "dark" ? "dark" : "light"
    );
})();