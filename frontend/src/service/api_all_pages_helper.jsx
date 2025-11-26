import * as url from "./api_all_pages_url";
import {
  get,
  post,
  put,
  del,
  delWithPayload,
  getExportData,
} from "./api_service";

export const postDemo = (data) => post(url.POST_DEMO, data);