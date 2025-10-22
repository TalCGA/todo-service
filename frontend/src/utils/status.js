export const STATUS_ORDER = ["open", "in_progress", "done"];

export const STATUS_LABELS = {
  open: "Open",
  in_progress: "In Progress",
  done: "Done",
};

export const STATUS_COLORS = {
  open: "#3b82f6",       
  in_progress: "#f59e0b",
  done: "#22c55e",       
};

export const statusInfo = (v) => ({
  label: STATUS_LABELS[v] ?? String(v),
  color: STATUS_COLORS[v] ?? "#6b7280", // default gray
});
