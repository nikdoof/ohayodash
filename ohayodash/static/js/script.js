function date() {
    let currentDate = new Date();
    let dateOptions = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
    };
    let date = currentDate.toLocaleDateString("en-GB", dateOptions);
    document.getElementById("header_date").innerHTML = date;
}

function greet() {
    let currentTime = new Date();
    let greet = Math.floor(currentTime.getHours() / 6);
    let greeting = "こんにちは!";
    switch (greet) {
        case 0:
            greeting = "おやすみなさい!";
            break;
        case 1:
            greeting = "おはようございます!";
            break;
        case 2:
            greeting = "こんにちは!";
            break;
        case 3:
            greeting = "こんばんは!";
            break;
    }
    document.getElementById("header_greet").innerHTML = greeting;
    document.title = greeting;
}

function loadFunctions() {
    date();
    greet();
}
