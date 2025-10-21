import axios from "axios";
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000",
});

export const listTasks = (params = {}) =>
  api.get("/tasks", { params }).then(r => r.data);

export const createTask = (payload) =>
  api.post("/tasks", payload).then(r => r.data);

export const patchTask = (id, partial) =>
  api.patch(`/tasks/${id}`, partial).then(r => r.data);

export const deleteTaskById = (id) =>
  api.delete(`/tasks/${id}`).then(r => r.status);

export const getStats = () =>
  api.get("/tasks/stats").then(r => r.data);
