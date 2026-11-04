// Permite conferir a senha digitada sem alterar o funcionamento do formulário.
document.querySelectorAll(".auth-mostrar-senha").forEach((botao) => {
    botao.addEventListener("click", () => {
        const campoId = botao.getAttribute("aria-controls");
        const campoSenha = document.getElementById(campoId);

        if (!campoSenha) {
            return;
        }

        const mostrarSenha = campoSenha.type === "password";

        campoSenha.type = mostrarSenha ? "text" : "password";
        botao.textContent = mostrarSenha ? "Ocultar" : "Mostrar";
        botao.setAttribute("aria-pressed", String(mostrarSenha));
    });
});
