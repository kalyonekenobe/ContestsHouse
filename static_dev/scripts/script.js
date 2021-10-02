function moveTo(target, args){
    if(target !== null)
        return window.scrollTo({ top: target.offsetTop - args['navbar_height']});
}

function showTooltip(element, timing = 0){
    const timingDelay = 50;
    let tooltipText = element.attributes['tooltip'].value;
    let tooltip = document.createElement("div");
    tooltip.classList.add('tooltip-container');
    tooltip.innerHTML = tooltipText;
    document.querySelector('body').append(tooltip);
    tooltip.style.left = (element.offsetLeft + element.offsetWidth / 2 - tooltip.offsetWidth / 2) + "px";
    tooltip.style.top = element.offsetTop - tooltip.offsetHeight - 5 + "px";
    tooltip.animate({ opacity: 1 }, timing);
    setTimeout(() => { tooltip.style.opacity = '1'; }, timing - timingDelay);
    element.onmouseleave = () => {
            tooltip.animate({ opacity: 0 }, timing);
            setTimeout(() => {
                tooltip.style.opacity = '0';
                tooltip.remove();
            }, timing - timingDelay);
    }
}

function moveUp(){
    return window.scrollTo({ top: 0 });
}

function HTMLFilePattern(file){
    let pattern = '<div class="form-file"><i class="bi bi-file-earmark mx-1"></i><span>' + file.name + '</span><i class="bi bi bi-x-circle text-danger ms-2 close"></i></div>';
    return pattern;
}

function sendAjaxQuery(method, url, data, content_type, csrftoken = ''){
    if(!content_type) content_type = content_type || 'application/x-www-form-urlencoded';
    let httpRequest = new XMLHttpRequest();
    httpRequest.open(method, url, true);
    httpRequest.setRequestHeader('X-CSRFToken', csrftoken);
    if(content_type === 'application/x-www-form-urlencoded')
        httpRequest.setRequestHeader('Content-Type', content_type);
    httpRequest.send(data);
    return httpRequest;
}

document.addEventListener('readystatechange', () => {
    if(document.readyState === 'complete')
        document.getElementById('page-loading').remove();
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
    let elementsWithTooltips = document.querySelectorAll('[tooltip]');
    for(let i = 0; i < elementsWithTooltips.length; i++){
        let element = elementsWithTooltips[i];
        element.onmouseenter = () => {
            showTooltip(element, 150);
        }
    }
    if(createComment){
        let replyToLinks = document.getElementsByClassName('comment-reply');
        let commentForm = document.getElementById('comment-form');
        let sendComment = document.getElementById('send-comment');
        let hideComment = document.getElementById('hide-comment-form');
        let addAttachedFiles = document.getElementById('add-attached-files');
        let attachedFilesInput = document.getElementById('attached-files');
        let attachedFilesContainer = document.getElementById('attached-files-container');
        let attachedFilesLabel = document.getElementById('attached-files-label');
        let attachedFiles = Array.from(attachedFilesInput.files);
        let url = sendComment.attributes['reference'].value;
        for(let i = 0; i < replyToLinks.length; i++){
            let link = replyToLinks[i];
            link.onclick = () => {
                let replyTo = link.attributes['reply-to'].value;
                commentForm.classList.remove('d-none');
                commentForm.reset();
                commentForm.querySelector('#reply-to').value = replyTo;
                moveTo(document.getElementById('comments-section'), {'navbar_height': navbarHeight});
                createComment.style.display = 'none';
            }
        }
        if(createComment){
            createComment.onclick = () => {
                commentForm.reset();
                commentForm.querySelector('#reply-to').value = null;
                commentForm.classList.remove('d-none');
                createComment.style.display = 'none';
            }
        }
        addAttachedFiles.onclick = () => {
            attachedFilesInput.click();
            attachedFilesInput.value = '';
            attachedFilesInput.onchange = () => {
                attachedFilesContainer.innerHTML = '';
                attachedFilesContainer.classList.remove('d-none');
                attachedFilesLabel.classList.remove('d-none');
                attachedFiles = Array.from(attachedFilesInput.files);
                for(let i = 0; i < attachedFilesInput.files.length; i++){
                    let file = attachedFilesInput.files[i];
                    attachedFilesContainer.innerHTML += HTMLFilePattern(file);
                }
                let attachedFilesHtml = commentForm.getElementsByClassName('form-file');
                if(attachedFilesHtml){
                    for(let i = 0; i < attachedFilesHtml.length; i++){
                        let fileHtml = attachedFilesHtml[i];
                        let closeButton = fileHtml.querySelector('.close');
                        closeButton.onclick = () => {
                            for(let j = 0; j < attachedFiles.length; j++){
                                let file = attachedFiles[j];
                                if(file.name == fileHtml.innerText){
                                    attachedFiles.splice(j, 1);
                                    fileHtml.remove();
                                }
                            }
                        }
                    }
                }
            }
        }
        hideComment.onclick = () => {
            commentForm.classList.add('d-none');
            createComment.style.display = 'inline-block';
        }
        sendComment.onclick = () => {
            let data = new FormData();
            data.append('author', commentForm.querySelector('[name="author"]').value);
            data.append('text', commentForm.querySelector('[name="text"]').value);
            data.append('reply_to', commentForm.querySelector('#reply-to').value);
            for(let i = 0; i < attachedFiles.length; i++){
                let file = attachedFiles[i];
                data.append('attached_files', file);
            }
            let httpRequest = sendAjaxQuery('POST', url, data, 'multipart/form-data', commentForm.querySelector('[name="csrfmiddlewaretoken"]').value);
            httpRequest.onreadystatechange = () => {
                if(httpRequest.readyState == XMLHttpRequest.DONE && httpRequest.status == 200) {
                    let httpResponse = JSON.parse(httpRequest.responseText);
                    if(httpResponse['response_code'] == 201){
                        document.getElementById('startup-comments').innerHTML = httpResponse['comment_tree'];
                        commentForm.classList.add('d-none');
                        attachedFilesContainer.classList.add('d-none');
                        attachedFilesLabel.classList.add('d-none');
                        createComment.style.display = 'inline-block';
                        replyToLinks = document.getElementsByClassName('comment-reply');
                        for(let i = 0; i < replyToLinks.length; i++){
                            let link = replyToLinks[i];
                            link.onclick = () => {
                                let replyTo = link.attributes['reply-to'].value;
                                commentForm.classList.remove('d-none');
                                commentForm.reset();
                                commentForm.querySelector('#reply-to').value = replyTo;
                                moveTo(document.getElementById('comments-section'), {'navbar_height': navbarHeight});
                                createComment.style.display = 'none';
                            }
                        }
                    }else if(httpResponse['response_code'] == 406){
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
            link.classList.add('disabled');
            let httpRequest = sendAjaxQuery('POST', linkReference, {}, false, Cookies.get('csrftoken'));
            httpRequest.onreadystatechange = () => {
                if(httpRequest.readyState == XMLHttpRequest.DONE && httpRequest.status == 200) {
                    let httpResponse = JSON.parse(httpRequest.responseText);
                    if(httpResponse['http_response'] == "follow"){
                        link.classList.remove('btn-primary');
                        link.classList.add('btn-light');
                        link.innerText = 'Відписатися';
                    }else if(httpResponse['http_response'] == "unfollow"){
                        link.classList.remove('btn-light');
                        link.classList.add('btn-primary');
                        link.innerText = 'Підписатися';
                    }
                    if(followers) followers.innerText = httpResponse['followers_quantity'];
                    link.classList.remove('disabled');
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