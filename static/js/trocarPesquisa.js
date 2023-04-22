function trocarPesquisa(e){
    if(e.target.value == 'turma') {
        var nome = document.querySelector('#nome');
        var turma = document.querySelector('#turma');

        e.target.nextElementSibling.placeholder = 'Pesquisar turma...'

        nome.classList.remove('selected');
        turma.classList.add('selected');
    }
    else{
        var nome = document.querySelector('#nome');
        var turma = document.querySelector('#turma');

        e.target.nextElementSibling.placeholder = 'Pesquisar nome...'

        turma.classList.remove('selected');
        nome.classList.add('selected');
    }
  }