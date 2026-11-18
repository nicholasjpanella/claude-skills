// Fake account API. Each call waits 600-1500ms and fails about one time in four.
const wait = () => new Promise(r => setTimeout(r, 600 + Math.random() * 900));
const flaky = () => { if (Math.random() < 0.25) throw new Error("network"); };

let account = { name: "Priya Shah", email: "priya.shah.bookkeeping.accounts@shahdesign-studio.co.uk" };

export async function getAccount() {
  await wait(); flaky();
  return { ...account };
}

export async function updateName(name) {
  await wait(); flaky();
  if (!name.trim()) throw new Error("empty");
  account.name = name.trim();
  return { ...account };
}

export async function updateEmail(email) {
  await wait(); flaky();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error("invalid");
  if (email === "taken@example.com") throw new Error("taken");
  account.email = email;
  return { ...account };
}

export async function deleteAccount(confirmEmail) {
  await wait(); flaky();
  if (confirmEmail !== account.email) throw new Error("mismatch");
  return { deleted: true };
}
