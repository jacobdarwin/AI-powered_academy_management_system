buildStudentLayout("AI assistant");
const $ = id => document.getElementById(id);
const chips = ["What is my attendance?", "How much fee do I have to pay?", "When is my next class?", "What deadlines do I have?", "Which drives can I apply to?"];
const bubble = (text, who) => { const node = document.createElement("div"); node.className = `bub ${who}`; node.textContent = text; $("msgs").appendChild(node); $("msgs").scrollTop = $("msgs").scrollHeight; return node; };
const ask = async text => { const clean = text.trim(); if (!clean) return; bubble(clean, "me"); const pending = bubble("Thinking...", "bot"); try { const response = await api.post("/assistant/messages", {message: clean}); pending.textContent = response.data?.message || response.data?.reply || "No response."; } catch (error) { pending.textContent = error.message || "Assistant unavailable."; saError(error); } };
$("chips").innerHTML = chips.map(item => `<button type="button" class="chip">${saEscape(item)}</button>`).join("");
$("chips").onclick = event => { if (event.target.classList.contains("chip")) ask(event.target.textContent); };
$("form").onsubmit = event => { event.preventDefault(); ask($("input").value); $("input").value = ""; };
bubble("Hello! Ask me about your academy information.", "bot");
