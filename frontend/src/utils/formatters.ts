export function formatPrice(value: number, unit = "BRL/L") {
  const unitSuffix = unit.toLowerCase().includes("m3") ? "/m³" : "/L";
  return `${new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(value)}${unitSuffix}`;
}

export function formatCompactPrice(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 3,
  }).format(value);
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(
    new Date(`${value}T00:00:00Z`),
  );
}
