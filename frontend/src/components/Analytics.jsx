import { STATUS_ORDER, statusInfo } from "../utils/status.js";
import { Paper } from "@mui/material";

export default function Analytics({ stats = {} }) {
  return (
    <section style={{ margin: "16px 0" }}>
        <Paper 
            elevation={0}
            sx={{
                border: "1px solid #ddd",
                borderRadius: 2,
                padding: 2,
                marginBottom: 2,
            }}
            >
            <h3 style={{ fontSize: "1.1rem", marginBottom: "4px" }}>Task Overview</h3>
            <p style={{ fontSize: "0.9rem", color: "#666", marginTop: 0, marginBottom: "12px" }}>
                Summary of tasks by current status:
            </p>

            <div
                style={{
                display: "flex",
                gap: "24px",
                flexWrap: "wrap",
                justifyContent: "flex-start",
                }}
            >
                {STATUS_ORDER.map((s) => {
                const { label, color } = statusInfo(s);
                const value = stats[s] ?? 0;
                return (
                    <div
                    key={s}
                    style={{
                        textAlign: "center",
                        minWidth: "80px",
                    }}
                    >
                    <div
                        style={{
                        fontSize: "1.3rem",
                        fontWeight: 600,
                        color,
                        lineHeight: "1.2",
                        }}
                    >
                        {value}
                    </div>
                    <div
                        style={{
                        fontSize: "0.9rem",
                        color: "#333",
                        opacity: 0.85,
                        marginTop: "2px",
                        }}
                    >
                        {label}
                    </div>
                    </div>
                );
                })}
            </div>
        </Paper>
    </section>
  );
}
