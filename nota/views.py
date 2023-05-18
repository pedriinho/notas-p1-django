import os
import requests
import json
import threading
import time
import datetime
import pytz
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Aluno, NotaAluno, DataAttNota, Turma
from django.contrib import messages
import pandas as pd
from django.contrib.auth.decorators import user_passes_test

def setStudentDataOnDatabase(students):
	student_table = Aluno.objects.all()

	for student in students:
		if(not student_table.filter(id_huxley=student['id_huxley']).exists()):
			new_student = Aluno(nome=student['nome'], id_huxley=student['id_huxley'])
			new_student.save()

def setStudentScoreListOnDatabase(userScores, list_number):
	for userScore in userScores:
		student = Aluno.objects.get(id_huxley=userScore['id_huxley'])
		setattr(student, 'lista'+str(list_number), userScore['score'])
		student.save()
	
def setStudentScoreTestsOnDatabase(userScores, list_number):
	for userScore in userScores:
		student = Aluno.objects.get(id_huxley=userScore['id_huxley'])
		if userScore['id_huxley'] == 42148 and list_number == 1:
			userScore['score'] += 2.9
		elif userScore['id_huxley'] == 40528 and list_number == 1:
			userScore['score'] = 9.2
		setattr(student, 'prova'+str(list_number), userScore['score'])
		student.save()

def setStudentScoreTestsReassessmentsOnDatabase(userScores, list_number):
	for userScore in userScores:
		student = Aluno.objects.get(id_huxley=userScore['id_huxley'])
		if list_number == 1:
			setattr(student, 'reav', userScore['score'])
		else:
			setattr(student, 'final', userScore['score'])
		student.save()

# gets each student's name and huxley id
def getStudentData(headers, id):
	data_url = f'https://www.thehuxley.com/api/v1/quizzes/{id}/users?max=100&offset=0'

	data_response = requests.get(data_url, headers=headers)

	students = []
	
	for students_data in data_response.json():
		students.append({
			'nome': students_data['name'].lower(),
			'id_huxley': students_data['id']
		})

	return students

def getScoreUrlsLists(id_lists):
	urls = []
	
	for id in id_lists:
		urls.append('https://www.thehuxley.com/api/v1/quizzes/' + str(id) + '/scores')

	return urls

def getScoreUrlsTests(ids_urls):
	urls = []
	
	for ids in ids_urls:
		urls.append('https://www.thehuxley.com/api/v1/quizzes/' + str(ids) + '/scores')

	return urls

def getUserScores(url, headers, type_score):
	userScores = []

	response = requests.get(url, headers=headers).json()
	for user in response:
		userScore = {}
		userScore['id_huxley'] = user['userId']

		score = 0
		for correctProblem in user['correctProblems']:
			if type_score == 1:
				score += correctProblem['score']
			else:
				score += round(correctProblem['partialScore'], 1) if correctProblem['partialScore'] > correctProblem['penalty'] else correctProblem['penalty']
		
		userScore['score'] = score

		userScores.append(userScore)

	return userScores

def get_token(username, password):
	headers = {
		"Content-type": "application/json"
	}
	data = {
		"username": username,
		"password": password
	}
	response = requests.post("https://thehuxley.com/api/login", headers=headers, data=json.dumps(data))
	token_json = response.json()
	return token_json["access_token"]

def getSubmission(access_token):
	turma = Turma.objects.get()
	id_list = [turma.id_lista1, turma.id_lista2, turma.id_lista3, turma.id_lista4, turma.id_lista5, turma.id_lista6, turma.id_lista7, turma.id_lista8]
	id_prova = [turma.id_prova1, turma.id_prova2, turma.id_prova3, turma.id_prova4]
	id_reavs = [turma.id_reav, turma.id_final]
	headers = {"Authorization": "Bearer " + access_token}

	students = getStudentData(headers, id_list[0])
	setStudentDataOnDatabase(students)

	urls_lists = getScoreUrlsLists(id_list)
	
	for index, url in enumerate(urls_lists):
		userScores = getUserScores(url, headers, 1)
		setStudentScoreListOnDatabase(userScores, index+1)

	urls_tests = getScoreUrlsTests(id_prova)

	for index, url in enumerate(urls_tests):
		userScores = getUserScores(url, headers, 2)
		setStudentScoreTestsOnDatabase(userScores, index+1)
	
	urls_tests_reassessments = getScoreUrlsTests(id_reavs)

	for index, url in enumerate(urls_tests_reassessments):
		userScores = getUserScores(url, headers, 2)
		setStudentScoreTestsReassessmentsOnDatabase(userScores, index+1)


def updateGrade():
	while True:
		try:
			login = os.environ['HUXLEY_USER']
			password = os.environ['HUXLEY_PASS']
			token = get_token(login, password)

			getSubmission(token)
			calcularAB1()
			calcularAB2()

			registro = 'Notas atualizadas por ultimo em: ' + datetime.datetime.now(pytz.utc).strftime('%d/%m/%Y %H:%M:%S')
			if(len(DataAttNota.objects.all()) >= 1):
				for data in DataAttNota.objects.all():
					DataAttNota.objects.get(registro=data.registro).delete()
			DataAttNota.objects.create(registro=registro).save()
		except:
			pass

@user_passes_test(lambda u: u.is_superuser)
def updateGradesThreading(request):
	gradesThread = threading.Thread(target=updateGrade)
	gradesThread.start()
	return redirect('resolution')
	

def index(request):
	return redirect('resolution')

# Lista de alunos com notas não calculadas
def resolution(request):
	data = {}
	colunas = ('Nome', 'Turma', 'Prova 1', 
	'Lista 1', 'Lista 2', 'Prova 2', 'Lista 3',
	'Lista 4', 'Prova 3', 'Lista 5', 'Lista 6',
	'Prova 4', 'Lista 7', 'Lista 8')

	lista = []
	for i in Aluno.objects.all():
		i.nome = i.nome.title()
		lista.append(i)

	alunos_ordenados = sorted(lista, key = lambda x: x.nome)

	data['alunos'] = alunos_ordenados
	data['colunas'] = colunas
	try:
		ultimoRegistro = DataAttNota.objects.get().registro.split(':')
		registro = ultimoRegistro[0] + ': ' + ultimoRegistro[1].split(' ')[1] + ' ' + str((int(ultimoRegistro[1].split(' ')[2])-3)%24) + ':' + ultimoRegistro[2] + ':' + ultimoRegistro[3]
		data['registro'] = registro
	except:
		pass


	return render(request, 'nota/resolution.html', data)

# Lista de alunos com notas calculadas
def notasAcumuladas(request):
	data = {}
	colunas = ('Nome', 'Turma', 'AB1', 'AB2', 
	'Reav', 'Final', 'Média', 'Situação',)

	lista = []
	for i in NotaAluno.objects.all():
		i.nome = i.nome.title()
		lista.append(i)

	alunos_ordenados = sorted(lista, key = lambda x: x.nome)

	data['alunos'] = alunos_ordenados
	data['colunas'] = colunas
	try:
		ultimoRegistro = DataAttNota.objects.get().registro.split(':')
		registro = ultimoRegistro[0] + ': ' + ultimoRegistro[1].split(' ')[1] + ' ' + str((int(ultimoRegistro[1].split(' ')[2])-3)%24) + ':' + ultimoRegistro[2] + ':' + ultimoRegistro[3]
		data['registro'] = registro
	except:
		pass

	return render(request, 'nota/notas.html', data)

# Calcula a média final
def calcularMediaFinal(aluno):
	alunoF = NotaAluno.objects.get(id_huxley = aluno.id_huxley)
	alunoF.mediaFinal = round(((alunoF.ab1 + alunoF.ab2)/2), 2)
	alunoF.save()

# Calcula a nota da AB1
def calcularAB1():
	alunos = Aluno.objects.all()

	for aluno in alunos:
		try:
			alunoF = NotaAluno.objects.get(id_huxley = aluno.id_huxley)
			notaAB1 = round(((((aluno.prova1 + aluno.prova2)*7)/20) + (((aluno.lista1 + aluno.lista2 + aluno.lista3 + aluno.lista4)*3)/59)), 2)
			if notaAB1 > 10:
				notaAB1 = 10
			alunoF.ab1 = notaAB1
			alunoF.save()
		except:
			notaAB1 = round(((((aluno.prova1 + aluno.prova2)*7)/20) + (((aluno.lista1 + aluno.lista2 + aluno.lista3 + aluno.lista4)*3)/59)), 2)
			if notaAB1 > 10:
				notaAB1 = 10
			alunoF = NotaAluno(nome = aluno.nome , id_huxley = aluno.id_huxley, ab1 = notaAB1)
			alunoF.save()

		calcularMediaFinal(aluno)

# Calcula a nota da AB2 e a média final		
def calcularAB2():
	alunos = Aluno.objects.all()

	for aluno in alunos:
		try:
			alunoF = NotaAluno.objects.get(id_huxley = aluno.id_huxley)
			notaAB2 = round(((((aluno.prova3 + aluno.prova4)*7)/20) + (((aluno.lista5 + aluno.lista6 + aluno.lista7 + aluno.lista8)*3)/66)), 2)
			if notaAB2 > 10:
				notaAB2 = 10
			alunoF.ab2 = notaAB2
			alunoF.mediaFinal = round( ((alunoF.ab1 + alunoF.ab2)/2), 2)
			if alunoF.mediaFinal >= 7:
				alunoF.situacao = 'APROVADO'
			alunoF.save()
		except:
			notaAB2 = round(((((aluno.prova3 + aluno.prova4)*7)/20) + (((aluno.lista5 + aluno.lista6 + aluno.lista7 + aluno.lista8)*3)/66)), 2)
			if notaAB2 > 10:
				notaAB2 = 10
			alunoF = NotaAluno(nome = aluno.nome, id_huxley=aluno.id_huxley, ab2 = notaAB2)
			alunoF.mediaFinal = round( ((alunoF.ab1 + alunoF.ab2)/2), 2)
			if alunoF.mediaFinal >= 7:
				alunoF.situacao = 'APROVADO'
			alunoF.save()

# Pesquisa por nome ou turma nas notas não calculadas
def searchNotaIndividual(request):
	if request.method == 'POST':
		search = request.POST['search']

		if request.POST['select'] == 'nome':
			result_search = Aluno.objects.filter(nome__contains=str(search).lower())
		elif request.POST['select'] == 'turma':
			result_search = Aluno.objects.filter(turma=search.upper())

		dados = {}
		colunas = ('Nome', 'Turma', 'Prova 1', 
		'Lista 1', 'Lista 2', 'Prova 2', 'Lista 3',
		'Lista 4', 'Prova 3', 'Lista 5', 'Lista 6',
		'Prova 4', 'Lista 7', 'Lista 8')

		lista = []
		for i in result_search:
			i.nome = i.nome.title()
			lista.append(i)

		alunos_ordenados = sorted(lista, key = lambda x: x.nome)

		dados['alunos'] = alunos_ordenados
		dados['colunas'] = colunas
		
		return render(request, 'nota/resolution.html', dados)
	else:
		return redirect('resolution')

# Pesquisa por nome ou turma nas notas calculadas
def searchNotaGeral(request):
	if request.method == 'POST':
		search = request.POST['search']

		if request.POST['select'] == 'nome':
			result_search = NotaAluno.objects.filter(nome__contains=str(search).lower())
		elif request.POST['select'] == 'turma':
			result_search = NotaAluno.objects.filter(turma=search.upper())

		dados = {}
		colunas = ('Nome', 'Turma', 'AB1', 'AB2', 
		'Reav', 'Final', 'Média', 'Situação',)

		lista = []
		for i in result_search:
			i.nome = i.nome.title()
			lista.append(i)

		alunos_ordenados = sorted(lista, key = lambda x: x.nome)

		dados['alunos'] = alunos_ordenados
		dados['colunas'] = colunas
		
		return render(request, 'nota/notas.html', dados)
	else:
		return redirect('notas')

# Modifica o id da prova ou lista de acordo com a turma
@user_passes_test(lambda u: u.is_superuser)
def changeClass(request):
	dados = {}
	ab1 = [
		['Prova 1'], ['Lista 1'], ['Lista 2'],
		['Prova 2'], ['Lista 3'], ['Lista 4']
	]
	ab2 = [
		['Prova 3'], ['Lista 5'],['Lista 6'],
		['Prova 4'], ['Lista 7'], ['Lista 8']
	]
	reavs = [
		['Reav'], ['Final']
	]

	dados['ab1'] = ab1
	dados['ab2'] = ab2
	dados['reavs'] = reavs

	if request.method == 'POST':
		if len(Turma.objects.all()) == 0:
			newClass = Turma(turma = request.POST['Turma'], id_prova1 = request.POST['Prova 1'],
			id_lista1 = request.POST['Lista 1'], id_lista2 = request.POST['Lista 2'],
			id_prova2 = request.POST['Prova 2'], id_lista3 = request.POST['Lista 3'],
			id_lista4 = request.POST['Lista 4'], id_prova3 = request.POST['Prova 3'],
			id_lista5 = request.POST['Lista 5'], id_lista6 = request.POST['Lista 6'],
			id_prova4 = request.POST['Prova 4'], id_lista7 = request.POST['Lista 7'],
			id_lista8 = request.POST['Lista 8'], id_reav = request.POST['Reav'],
			id_final = request.POST['Final'])
			newClass.save()
		else:

			turma = Turma.objects.get()

			
			turma.turma = request.POST['Turma']
			turma.id_prova1 = request.POST['Prova 1']
			turma.id_lista1 = request.POST['Lista 1']
			turma.id_lista2 = request.POST['Lista 2']
			turma.id_prova2 = request.POST['Prova 2']
			turma.id_lista3 = request.POST['Lista 3']
			turma.id_lista4 = request.POST['Lista 4']
			turma.id_prova3 = request.POST['Prova 3']
			turma.id_lista5 = request.POST['Lista 5']
			turma.id_lista6 = request.POST['Lista 6']
			turma.id_prova4 = request.POST['Prova 4']
			turma.id_lista7 = request.POST['Lista 7']
			turma.id_lista8 = request.POST['Lista 8']
			turma.id_reav = request.POST['Reav']
			turma.id_final = request.POST['Final']
			turma.save()

			dados['turma'] = turma.turma
			dados['ab1'][0].append(turma.id_prova1)
			dados['ab1'][1].append(turma.id_lista1)
			dados['ab1'][2].append(turma.id_lista2)
			dados['ab1'][3].append(turma.id_prova2)
			dados['ab1'][4].append(turma.id_lista3)
			dados['ab1'][5].append(turma.id_lista4)
			dados['ab2'][0].append(turma.id_prova3)
			dados['ab2'][1].append(turma.id_lista5)
			dados['ab2'][2].append(turma.id_lista6)
			dados['ab2'][3].append(turma.id_prova4)
			dados['ab2'][4].append(turma.id_lista7)
			dados['ab2'][5].append(turma.id_lista8)
			dados['reavs'][0].append(turma.id_reav)
			dados['reavs'][1].append(turma.id_final)
		
		notasAlunos = NotaAluno.objects.all()
		for aluno in notasAlunos:
			aluno.delete()

		alunos = Aluno.objects.all()
		for aluno in alunos:
			aluno.delete()
		
		return render(request, 'nota/changeClass.html', dados)
	else:
		if(len(Turma.objects.all()) != 0):
			turma = Turma.objects.first()
			dados['turma'] = turma.turma
			dados['ab1'][0].append(turma.id_prova1)
			dados['ab1'][1].append(turma.id_lista1)
			dados['ab1'][2].append(turma.id_lista2)
			dados['ab1'][3].append(turma.id_prova2)
			dados['ab1'][4].append(turma.id_lista3)
			dados['ab1'][5].append(turma.id_lista4)
			dados['ab2'][0].append(turma.id_prova3)
			dados['ab2'][1].append(turma.id_lista5)
			dados['ab2'][2].append(turma.id_lista6)
			dados['ab2'][3].append(turma.id_prova4)
			dados['ab2'][4].append(turma.id_lista7)
			dados['ab2'][5].append(turma.id_lista8)
			dados['reavs'][0].append(turma.id_reav)
			dados['reavs'][1].append(turma.id_final)
		else:
			dados['turma'] = 'Sem Turma Registrada'
		return render(request, 'nota/changeClass.html', dados)

# Adicinar a turma aos alunos (EC - CC)
@user_passes_test(lambda u: u.is_superuser)	
def addTurmaAluno(request):
	if request.method == 'POST':
		for turmaAluno in request.FILES['arquivo'].read().decode('utf-8').split('\r\n'):
			try:
				aluno = Aluno.objects.get(id_huxley = turmaAluno.split('-')[0])
				aluno.turma = turmaAluno.split('-')[1].upper()
				aluno.save()

				notaAluno = NotaAluno.objects.get(id_huxley = turmaAluno.split('-')[0])
				notaAluno.turma = turmaAluno.split('-')[1].upper()
				notaAluno.save()
			except:
				pass
		return render(request, 'nota/addTurmaAluno.html')
	else:
		return render(request, 'nota/addTurmaAluno.html')
