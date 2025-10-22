import { useEffect, useState } from "react";
import { Container, Typography, Box } from "@mui/material";
import {
  listTasks,
  createTask,
  patchTask,
  deleteTaskById,
  getStats,
} from "./api.js";
import TaskForm from "./components/TaskForm.jsx";
import TaskList from "./components/TaskList.jsx";
import Analytics from "./components/Analytics.jsx";


export default function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setLoading(true);
      setError("");

      const [list, s] = await Promise.all([
        listTasks({
          sort: "created_at",
          direction: "desc",
          limit: 50,
          offset: 0,
        }),
        getStats(),
      ]);

      setTasks(list);
      setStats(s);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const onCreate = async (payload) => {
    try {
      await createTask(payload);
      await refresh();
    } catch (e) {
      alert(e?.response?.data?.detail || "Create failed");
    }
  };

  const onChangeStatus = async (id, status) => {
    try {
      await patchTask(id, { status });
      await refresh();
    } catch (e) {
      alert(e?.response?.data?.detail || "Update failed");
    }
  };

  const onDelete = async (id) => {
    try {
      await deleteTaskById(id);
      await refresh();
    } catch (e) {
      alert(e?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 2 }}>
        Tasks
      </Typography>

      <TaskForm onCreate={onCreate} disabled={loading} />

      {error && (
        <Typography color="error" sx={{ mt: 1, mb: 2 }}>
          {String(error)}
        </Typography>
      )}

      <Analytics stats={stats} />

      {loading ? (
        <Typography sx={{ mt: 2 }}>Loading…</Typography>
      ) : (
        <TaskList
          items={tasks}
          onChangeStatus={onChangeStatus}
          onDelete={onDelete}
        />
      )}
    </Container>
  );
}
