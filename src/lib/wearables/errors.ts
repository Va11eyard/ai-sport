export class AdapterError extends Error {
  constructor(
    readonly code: "source_not_configured" | "not_found" | "invalid_snapshot",
    message: string,
  ) {
    super(message);
    this.name = "AdapterError";
  }
}