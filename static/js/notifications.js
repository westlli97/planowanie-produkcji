(() => {
    const container = document.getElementById("toast-container");
    if (!container || !window.WebSocket) return;

    const scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${scheme}://${window.location.host}/ws/notifications/`);

    socket.addEventListener("message", (event) => {
        let notification;
        try {
            notification = JSON.parse(event.data);
        } catch {
            return;
        }

        const toast = document.createElement("div");
        toast.className = "rounded-lg border border-teal-200 bg-white p-4 shadow-lg";
        toast.setAttribute("role", "status");

        const title = document.createElement("p");
        title.className = "font-semibold text-slate-900";
        title.textContent = notification.title || "Powiadomienie";
        toast.append(title);

        if (notification.body) {
            const body = document.createElement("p");
            body.className = "mt-1 text-sm text-slate-700";
            body.textContent = notification.body;
            toast.append(body);
        }

        if (notification.url && notification.url.startsWith("/")) {
            const link = document.createElement("a");
            link.className = "mt-2 inline-block min-h-11 py-2 text-sm font-semibold text-teal-800";
            link.href = notification.url;
            link.textContent = "Otwórz";
            toast.append(link);
        }

        container.prepend(toast);
        window.setTimeout(() => toast.remove(), 10000);
    });
})();
