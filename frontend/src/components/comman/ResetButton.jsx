import { useResetStatus } from "../../hook/useResetStatus";

const ResetButton = ({ onClick, tableState, columnFilters, globalSearch, selectedRows }) => {
  const active = useResetStatus({ tableState, columnFilters, globalSearch, selectedRows });

  return (
    <button
      onClick={onClick}
      className="btn btn-sm py-1 fw-medium"
      style={{
        backgroundColor: active ? "#5a6c5b" : "#fff",
        color: active ? "#fff" : "#000",
        border: "1px solid #5a6c5b",
      }}
    >
      Reset
    </button>
  );
};

export default ResetButton;
