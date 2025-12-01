// useResetStatus.js
export const useResetStatus = ({
  tableState,
  columnFilters = {},
  globalSearch,
  selectedRows = []
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

  const hasSelection = Array.isArray(selectedRows) && selectedRows.length > 0;

  return hasFilters || hasSearch || hasSort || hasSelection;
};
