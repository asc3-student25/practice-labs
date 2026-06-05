const API_BASE = "http://localhost:5000/api/users";

async function createUser(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    username: form.username.value,
    email: form.email.value,
  };
  const response = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    console.error("create failed", await response.json());
    return;
  }
  const user = await response.json();
  appendUser(user);
  form.reset();
}

function appendUser(user) {
  const li = document.createElement("li");
  li.textContent = `${user.username} <${user.email}>`;
  document.getElementById("user-list").appendChild(li);
}

document.getElementById("create-user-form").addEventListener("submit", createUser);
