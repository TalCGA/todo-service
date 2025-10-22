import React from "react"; 
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
  Select,
  MenuItem,
  IconButton,
  Stack,
} from "@mui/material";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { formatDate } from "../utils/format.js";
import { statusInfo, STATUS_ORDER } from "../utils/status.js";

export default function TaskList({ items, onChangeStatus, onDelete }) {
  if (!items?.length) {
    return <p style={{ opacity: 0.7 }}>No tasks</p>;
  }

  return (
    <TableContainer component={Paper} sx={{ 
        overflowX: "auto", border: "1px solid #ddd",
        borderRadius: 2,
        padding: 2,
        marginBottom: 2, 
    }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell width="24%">Title</TableCell>
            <TableCell width="40%">Description</TableCell>
            <TableCell width="16%">Status</TableCell>
            <TableCell width="12%">Created</TableCell>
            <TableCell width="8%" align="right">Actions</TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {items.map((t) => {
            const { label, color } = statusInfo(t.status);
            return (
            <TableRow key={t.id} hover>
              <TableCell sx={{ verticalAlign: "top" }}>
                {t.title}
              </TableCell>

              <TableCell sx={{ verticalAlign: "top", color: "text.secondary" }}>
                {t.description ?? "-"}
              </TableCell>

              <TableCell>
                <Select
                    size="small"
                    value={t.status}
                    onChange={(e) => onChangeStatus(t.id, e.target.value)}
                    sx={{
                    backgroundColor: color,
                    color: "white",
                    fontWeight: 600,
                    borderRadius: 1,
                    "& .MuiSelect-icon": { color: "white" },
                    }}
                >
                    {STATUS_ORDER.map((s) => {
                    const { label } = statusInfo(s);
                    return (
                        <MenuItem key={s} value={s}>
                        {label}
                        </MenuItem>
                    );
                    })}
                </Select>
                </TableCell>

              <TableCell sx={{ verticalAlign: "top" }}>
                {formatDate(t.created_at)}
              </TableCell>

              <TableCell align="right" sx={{ verticalAlign: "top" }}>
                <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                  <IconButton
                    aria-label="Delete task"
                    color="error"
                    onClick={() => {
                      if (window.confirm("Confirm delete?")) onDelete(t.id);
                    }}
                  >
                    <DeleteOutlineIcon />
                  </IconButton>
                </Stack>
              </TableCell>
            </TableRow>
          )})}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
