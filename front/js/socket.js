//socket js method

export const socket = io("https://localhost:8080", {
  transports: ["websocket"],
  secure: true
});


sendRequest("query_state_summary", { client_id: "ALL" })
  .then(data => {
    showSummary(data);
  })
  .catch(err => {
    alert(err.message);
  });
