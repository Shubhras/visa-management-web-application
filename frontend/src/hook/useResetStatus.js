// useResetStatus.js
export const useResetStatus = ({
  tableState,
  columnFilters = {},
  globalSearch,
}) => {
  // Check active filters ONLY if the component has filters
  const hasFilters =
    columnFilters &&
    Object.values(columnFilters).some((v) => Array.isArray(v) && v.length > 0);

  const hasSearch = globalSearch?.trim() !== "";

  const hasSort = !(
    tableState.sort.length === 1 &&
    tableState.sort[0].field === "created_at" &&
    tableState.sort[0].order === "desc"
  );

  return hasFilters || hasSearch || hasSort;
};
