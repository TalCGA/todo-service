export default function ConfirmButton({
  onConfirm,
  children,
  message = "Confirm delete?",
}) {
  return (
    <button onClick={() => window.confirm(message) && onConfirm()}>
      {children}
    </button>
  );
}
