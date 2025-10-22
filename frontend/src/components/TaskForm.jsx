import React from "react"; 
import { useState } from "react";
import {
  Box,
  Paper,
  Stack,
  TextField,
  Button,
  Typography,
} from "@mui/material";

export default function TaskForm({ onCreate, disabled }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    await onCreate({
      title: title.trim(),
      description: description || null,
      status: "open",
    });

    setTitle("");
    setDescription("");
  };

  return (
    <Paper 
    component="form" onSubmit={submit} elevation={0}
    sx={{
        border: "1px solid #ddd",
        borderRadius: 2,
        padding: 2,
        marginBottom: 2,
    }}>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Add Task
      </Typography>

      <Stack spacing={2} maxWidth={600}>
        <TextField
          label="Title"
          placeholder="Enter task title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          inputProps={{ minLength: 1, maxLength: 255 }}
        />

        <TextField
          label="Description"
          placeholder="Optional notes"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          multiline
          minRows={3}
        />

        <Box>
          <Button type="submit" variant="contained" disabled={disabled}>
            Add Task
          </Button>
        </Box>
      </Stack>
    </Paper>
  );
}
