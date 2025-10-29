//chapter one questions
let userName = prompt("What is your name?");
let password = prompt("What is your password?");
let confirmPassword = prompt("Please confirm your password");
if (password === confirmPassword) {
    alert("Welcome " + userName + "!");
}