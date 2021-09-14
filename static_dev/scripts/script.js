function moveTo(target, args){
    if(target !== null)
        return window.scrollTo({ top: target.offsetTop - args['navbar_height']});
}

function moveUp(){
    return window.scrollTo({ top: 0 });
}

function sendAjaxQuery(method, url, data, csrftoken = ''){
    let httpRequest = new XMLHttpRequest();
    httpRequest.open(method, url, true);
    httpRequest.setRequestHeader('X-CSRFToken', csrftoken);
    httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    httpRequest.send(data);
    return httpRequest;
}

document.addEventListener('readystatechange', () => {
    if(document.readyState == 'complete'){
        document.getElementById('page-loading').remove();
    }
});

window.onload = function() {
    let navbarTheme = 'light';
    let references = document.getElementsByClassName('reference');
    let sections = document.getElementsByTagName('section');
    let navbar = document.getElementById('navbar'), navbarHeight = navbar.offsetHeight, iterator = 0;
    let scrollProgress = document.getElementById('site-loading');
    let mainPageLocation = document.getElementById('welcome-section');
    let scrollTopButton = document.getElementById('scroll-top');
    let followLinks = document.getElementsByClassName('follow-link');
    let createComment = document.getElementById('create-comment');
    if(createComment){
        let replyToLinks = document.getElementsByClassName('comment-reply');
        let commentForm = document.getElementById('comment-form');
        let sendComment = document.getElementById('send-comment');
        let hideComment = document.getElementById('hide-comment-form');
        let addAttachedFiles = document.getElementById('add-attached-files');
        let url = sendComment.attributes['reference'].value;
        for(let i = 0; i < replyToLinks.length; i++){
            let link = replyToLinks[i];
            link.onclick = () => {
                let replyTo = link.attributes['reply-to'].value;
                commentForm.classList.remove('d-none');
                commentForm.querySelector('#reply-to').value = replyTo;
                moveTo(document.getElementById('comments-section'), {'navbar_height': navbarHeight});
                createComment.style.display = 'none';
            }
        }
        if(createComment){
            createComment.onclick = () => {
                commentForm.classList.remove('d-none');
                createComment.style.display = 'none';
            }
        }
        hideComment.onclick = () => {
            commentForm.classList.add('d-none');
            createComment.style.display = 'inline-block';
        }
        sendComment.onclick = () => {
            let data = {
                'author': commentForm.querySelector('[name="author"]').value,
                'text': commentForm.querySelector('[name="text"]').value,
                'reply_to': commentForm.querySelector('#reply-to').value,
                'attached_files': commentForm.querySelectorAll('attached-file'),
            }
            data = JSON.stringify(data);
            let httpRequest = sendAjaxQuery('POST', url, data, commentForm.querySelector('[name="csrfmiddlewaretoken"]').value);
            httpRequest.onreadystatechange = () => {
                if(httpRequest.readyState == XMLHttpRequest.DONE && httpRequest.status == 200) {
                    let httpResponse = JSON.parse(httpRequest.responseText);
                    if(httpResponse == 201){
                        commentForm.classList.add('d-none');
                        createComment.style.display = 'inline-block'
                    }else if(httpResponse == 406){
                        alert("Error");
                    }
                }
            }
        }
    }
    for(let i = 0; i < followLinks.length; i++){
        let link = followLinks[i];
        let followers = document.getElementById(link.attributes['startup-id'].value);
        let linkReference = link.attributes['reference'].value;
        link.onclick = () => {
            let httpRequest = sendAjaxQuery('POST', linkReference, {}, Cookies.get('csrftoken'));
            httpRequest.onreadystatechange = () => {
                if(httpRequest.readyState == XMLHttpRequest.DONE && httpRequest.status == 200) {
                    let httpResponse = JSON.parse(httpRequest.responseText);
                    if(httpResponse['action'] == "follow"){
                        link.classList.remove('btn-primary');
                        link.classList.add('btn-light');
                        link.innerText = 'Відписатися';
                    }else if(httpResponse['action'] == "unfollow"){
                        link.classList.remove('btn-light');
                        link.classList.add('btn-primary');
                        link.innerText = 'Підписатися';
                    }
                    if(followers) followers.innerText = httpResponse['followers_quantity'];
                }
            }
        }
    }
    scrollProgress.style.width = window.scrollY / (document.body.clientHeight - window.innerHeight) * 100 + "%";
    for(let i = 0; i < references.length; i++){
        let reference = references[i];
        reference.onclick = () => {
            let targetId = reference.attributes['refer-to'].value;
            moveTo(document.getElementById(targetId), {'navbar_height': navbarHeight - 1, });
        }
    }
    for(let i = sections.length - 1; i >= 0; i--){
        let section = sections[i];
        if(window.scrollY >= section.offsetTop){
            iterator = i + 1;
            navbar.classList.remove(navbarTheme);
            navbarTheme = section.attributes['navbar-theme'].value
            navbar.classList.add(navbarTheme);
            break;
        }
    }
    if(mainPageLocation){
        if(window.scrollY == 0){
            navbar.classList.remove(navbarTheme);
            navbarTheme = 'transparent';
            navbar.classList.add(navbarTheme);
            iterator = 0;
        }
    }
    window.onscroll = function() {
        /* navbar script */
        let positionY = window.scrollY;
        scrollProgress.style.width = positionY / (document.body.clientHeight - window.innerHeight) * 100 + "%";
        if(iterator - 1 >= 0){
            if(positionY + navbarHeight <= sections[iterator - 1].offsetTop){
                navbar.classList.remove(navbarTheme);
                if(iterator - 2 >= 0)
                    navbarTheme = sections[iterator - 2].attributes['navbar-theme'].value;
                else
                    navbarTheme = 'light';
                navbar.classList.add(navbarTheme);
                iterator--;
            }
        }
        if(iterator < sections.length){
            if(positionY + navbarHeight > sections[iterator].offsetTop){
                navbar.classList.remove(navbarTheme);
                navbarTheme = sections[iterator].attributes['navbar-theme'].value;
                navbar.classList.add(navbarTheme);
                iterator++;
            }
        }
        if(mainPageLocation){
            if(positionY == 0){
                navbar.classList.remove(navbarTheme);
                navbarTheme = 'transparent';
                navbar.classList.add(navbarTheme)
                iterator = 0;
            }
        }
        /* end navbar script */
        /* scroll top button script */
        if(positionY > 100){
            scrollTopButton.style.display = 'flex';
            scrollTopButton.onclick = () => {
                moveUp();
            };
        }else{
            scrollTopButton.style.display = 'none';
        }
        /* end scroll top button script */
    }
}