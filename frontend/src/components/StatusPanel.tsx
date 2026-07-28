interface StatusPanelProps {
  kind: "loading" | "error" | "empty";
  title: string;
  message: string;
  onRetry?: () => void;
}

export function StatusPanel({
  kind,
  title,
  message,
  onRetry,
}: StatusPanelProps) {
  return (
    <section
      className={`status-panel status-panel--${kind}`}
      role={kind === "error" ? "alert" : "status"}
      aria-live="polite"
    >
      {kind === "loading" && <span className="spinner" aria-hidden="true" />}
      <div>
        <h2>{title}</h2>
        <p>{message}</p>
      </div>
      {onRetry && (
        <button
          className="button button--secondary"
          type="button"
          onClick={onRetry}
        >
          Tentar novamente
        </button>
      )}
    </section>
  );
}
