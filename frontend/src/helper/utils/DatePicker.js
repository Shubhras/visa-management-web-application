import DatePicker from "react-datepicker";
import { format } from "date-fns";
import "react-datepicker/dist/react-datepicker.css";

// Safe date parser
const safeDate = (value) => {
  if (!value) return null;
  const d = new Date(value);
  return isNaN(d.getTime()) ? null : d;
};

// Max days in a month
const getMaxDays = (month, year) => new Date(year, month, 0).getDate();

// Format DD/MM/YY progressively
const formatRaw = (raw) => {
  raw = raw.replace(/[^0-9]/g, "").slice(0, 6);

  if (raw.length >= 3) {
    let mm = parseInt(raw.slice(2, 4));
    if (!mm || mm < 1) mm = 1;
    if (mm > 12) mm = 12;
    raw = raw.slice(0, 2) + mm.toString().padStart(2, "0") + raw.slice(4);
  }

  if (raw.length >= 4) {
    let yy = parseInt(raw.slice(4, 6)) || 0;
    let fullYear = yy <= 49 ? 2000 + yy : 1900 + yy;

    let dd = parseInt(raw.slice(0, 2));
    const mm = parseInt(raw.slice(2, 4));
    const max = getMaxDays(mm, fullYear);

    if (!dd || dd < 1) dd = 1;
    if (dd > max) dd = max;

    raw = dd.toString().padStart(2, "0") + raw.slice(2);
  }

  if (raw.length <= 2) return raw;
  if (raw.length <= 4) return `${raw.slice(0, 2)}/${raw.slice(2)}`;
  return `${raw.slice(0, 2)}/${raw.slice(2, 4)}/${raw.slice(4)}`;
};

// Convert 6-digit raw to ISO yyyy-mm-dd
const convertToISO = (raw) => {
  if (raw.length !== 6) return "";
  const dd = raw.slice(0, 2);
  const mm = raw.slice(2, 4);
  const yy = raw.slice(4, 6);
  const yyyy = parseInt(yy) <= 49 ? `20${yy}` : `19${yy}`;
  return `${yyyy}-${mm}-${dd}`;
};

const CommonDatePicker = ({ value, onChange = () => {}, error }) => {
  return (
    <DatePicker
      selected={safeDate(value)}
      openToDate={safeDate(value) || new Date()}
      onChange={(date) => {
        const iso = date ? format(date, "yyyy-MM-dd") : "";
        onChange(iso);
      }}
      dateFormat="dd/MM/yy"
      placeholderText="dd/mm/yy"
      customInput={
        <input
          className={`form-control radius-8 ${error ? "is-invalid" : ""}`}
        />
      }
      onKeyDown={(e) => {
        const allowed = [
          "Backspace",
          "Delete",
          "ArrowLeft",
          "ArrowRight",
          "Tab",
        ];
        if (!isNaN(parseInt(e.key))) return;
        if (allowed.includes(e.key)) return;
        e.preventDefault();
      }}
      onChangeRaw={(e) => {
        if (!e || !e.target || typeof e.target.value !== "string") return;

        const inputType = e.nativeEvent?.inputType;
        const input = e.target;

        const cursorPos = input.selectionStart;
        let rawDigits = e.target.value.replace(/[^0-9]/g, "");

        // Allow deleting without forcing formatting
        if (
          inputType === "deleteContentBackward" ||
          inputType === "deleteContentForward"
        ) {
          onChange(e.target.value);
          setTimeout(() => {
            input.setSelectionRange(cursorPos, cursorPos);
          }, 0);
          return;
        }

        rawDigits = rawDigits.slice(0, 6);

        const formatted = formatRaw(rawDigits);
        e.target.value = formatted;

        // Reposition cursor correctly (important)
        let newCursorPos = cursorPos;

        if (formatted[cursorPos - 1] === "/") {
          newCursorPos = cursorPos + 1;
        }

        setTimeout(() => {
          input.setSelectionRange(newCursorPos, newCursorPos);
        }, 0);

        // Auto convert to ISO when full
        if (rawDigits.length === 6) {
          const iso = convertToISO(rawDigits);
          onChange(iso);
        }
      }}
    />
  );
};

export default CommonDatePicker;
