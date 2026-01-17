
// Shows an error message inside a div (like reg_js_error, ev_js_error, pf_js_error)
function showError(id, msg) {
  const box = document.getElementById(id);
  if (!box) return;
  box.style.display = "block";
  box.textContent = msg;
}

// Hides the error div and clears the message
function hideError(id) {
  const box = document.getElementById(id);
  if (!box) return;
  box.style.display = "none";
  box.textContent = "";
}

// Checks the assignment password rules:
// - at least 10 characters
// - at least 1 uppercase, 1 lowercase, 1 digit
function passwordValid(p) {
  if (p.length < 10) return false;
  if (!/[A-Z]/.test(p)) return false;
  if (!/[a-z]/.test(p)) return false;
  if (!/[0-9]/.test(p)) return false;
  return true;
}

// When user selects Paid/Free, show or hide the fee input box
function toggleFee() {
  const paid = document.querySelector('input[name="fee_type"][value="paid"]');
  const feeBox = document.getElementById("feeBox");
  if (!feeBox || !paid) return;
  feeBox.style.display = paid.checked ? "block" : "none";
}

// Registration form validation:
// makes sure fields are not empty + password matches the rule
function validateRegister() {
  hideError("reg_js_error");
  const u = document.getElementById("reg_username").value.trim();
  const p = document.getElementById("reg_password").value;
  const n = document.getElementById("reg_fullname").value.trim();
  const e = document.getElementById("reg_email").value.trim();

  // mandatory fields check
  if (!u || !p || !n || !e) {
    showError("reg_js_error", "All fields are mandatory.");
    return false; }
  // password rule check
  if (!passwordValid(p)) {
    showError("reg_js_error", "Password must be 10+ chars with uppercase, lowercase, digit.");
    return false; }
  return true; // allow submit
}


// Event creation validation:
// checks mandatory fields, at least one society selected,
// and if paid is selected then fee must be numeric
function validateEvent() {
  hideError("ev_js_error");
  const name = document.getElementById("ev_name").value.trim();
  const time = document.getElementById("ev_time").value.trim();
  const desc = document.getElementById("ev_desc").value.trim();
  // paid/free radio check (paid means fee must be given)
  const paid = document.querySelector('input[name="fee_type"][value="paid"]').checked;
  // fee input might be hidden, but we still read it if exists
  const fee = document.getElementById("ev_fee") ? document.getElementById("ev_fee").value.trim() : "";

  // number of societies checked
  const checked = document.querySelectorAll('input[name="societies"]:checked').length;

  // base required fields
  if (!name || !time || !desc) {
    showError("ev_js_error", "All event fields are mandatory.");
    return false; }

  // must select at least one society for the event
  if (checked === 0) {
    showError("ev_js_error", "Select at least one society.");
    return false; }

  // if paid, fee must be a number (integer or decimal)
  if (paid) {
    if (!/^\d+(\.\d+)?$/.test(fee)) {
      showError("ev_js_error", "Fee must be a number (integer or decimal).");
      return false; }
  }
  return true;
}

// Profile update validation:
// fullname and email cannot be empty.
// password is optional, but if user enters a new password, it must satisfy rules.
function validateProfile() {
  hideError("pf_js_error");
  const n = document.getElementById("pf_fullname").value.trim();
  const e = document.getElementById("pf_email").value.trim();
  const p = document.getElementById("pf_password").value;

  if (!n || !e) {
    showError("pf_js_error", "Name and email cannot be empty.");
    return false; }

  // only validate password if user typed something
  if (p && !passwordValid(p)) {
    showError("pf_js_error", "New password must be 10+ chars with uppercase, lowercase, digit.");
    return false; }
  return true;
}
