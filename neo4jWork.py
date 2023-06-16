import streamlit as st
from py2neo import *
import csv
import pandas as pd
from streamlit_option_menu import option_menu

graph = Graph("http://127.0.0.1:7474", auth=("neo4j", "root"))


def import_csv():
	st.header('导入csv文件')
	uploaded_file = st.file_uploader("请选择文件")
	if uploaded_file is not None:
		if st.button('开始导入数据库'):
			if uploaded_file is not None:
				file_contents = uploaded_file.read().decode("utf-8").splitlines()
				reader = csv.reader(file_contents)
				row1 = next(reader)
				st.write(row1)
				data1 = []
				row_num = 0
				for row in reader:
					if row_num == 0:
						row_num += 1
					s_node = Node(row1[0], name=row[0])
					e_node = Node(row1[2], name=row[2])
					r = Relationship(s_node, row[1], e_node)
					graph.merge(s_node, row1[0], "name")
					graph.merge(e_node, row1[2], "name")  # node,label,primary key
					graph.merge(r)
					data1.append(row)
				st.write('插入csv文件成功')
				df = pd.DataFrame(data1, columns=[row1[0], row1[1], row1[2]])
				st.write(df)
	else:
		st.warning('请选择csv文件！')


def insert():
	st.header('插入节点')
	label = st.text_input('请输入标签名称：')
	nm = st.text_input('请输入节点名称：')
	if st.button('确定'):
		if len(label) != 0 and len(nm) != 0:
			a = Node(label, name=nm)
			graph.create(a)
			st.write('插入成功！')
		else:
			st.warning('请输入数据！')


def insert_relation():
	st.header('插入关系')
	label1 = st.text_input('请输入第一个节点标签：')
	nm1 = st.text_input('请输入第一个节点名称：')
	label2 = st.text_input('请输入第二个节点标签：')
	nm2 = st.text_input('请输入第二个节点名称：')
	relation = st.text_input('请输入关系：')
	if st.button('确定'):
		if len(nm1) != 0 and len(nm2) != 0 and len(relation) and len(label2) != 0 and len(label1) != 0:
			node1 = graph.nodes.match(label1, name=nm1).first()
			node2 = graph.nodes.match(label2, name=nm2).first()
			a_to_b = Relationship(node1, relation, node2)
			graph.create(a_to_b)
			st.write('插入成功！')
		else:
			st.warning('请输入数据！')


def delete():
	st.header('删除节点')
	del_lab = st.text_input('请输入需要删除节点的标签')
	delete1 = st.text_input('请输入需要删除的节点')
	if st.button('确定'):
		if len(delete1) != 0 and len(del_lab) != 0:
			matcher = NodeMatcher(graph)
			node = matcher.match(del_lab).where(name=delete1).first()
			graph.delete(node)
			st.write('删除成功！')
		else:
			st.warning('请输入数据！')


def delete_relation():
	st.header('删除关系')
	label1 = st.text_input('请输入第一个节点标签：')
	nm1 = st.text_input('请输入第一个节点名称：')
	label2 = st.text_input('请输入第二个节点标签：')
	nm2 = st.text_input('请输入第二个节点名称：')
	relation = st.text_input('请输入关系：')
	if st.button('确定'):
		if len(nm1) != 0 and len(nm2) != 0 and len(relation) and len(label2) != 0 and len(label1) != 0:
			relation_matcher = RelationshipMatcher(graph)
			node1 = graph.nodes.match(label1, name=nm1).first()
			node2 = graph.nodes.match(label2, name=nm2).first()
			result = relation_matcher.match({node1, node2}, r_type=None).first()
			graph.separate(result)
			st.write('删除关系成功！')
		else:
			st.warning('请输入数据！')


def delete_all():
	st.header('删库跑路喽！')
	if st.button('一键删除所有数据？'):
		graph.delete_all()
		st.text('已全部删除')


def update():
	st.header('修改节点名称')
	update_label = st.text_input('请输入需要修改的节点名称的标签：', key='up_lab')
	update_name = st.text_input('请输入需要修改的节点名称的标签：', key='up_nm')
	new_name = st.text_input('请输入修改后的名字：', key='n_nm')
	if st.button('确定'):
		if len(update_label) != 0 and len(update_name) != 0 and len(new_name) != 0:
			node = graph.nodes.match(update_label, name=update_name).first()
			node["name"] = new_name
			graph.push(node)
			st.write('修改成功！')
		else:
			st.warning('请输入数据！')


def find():
	st.header('根据标签查询节点')
	nm = st.text_input('请输入需要查询节点的标签：')
	node_matcher = NodeMatcher(graph)
	if st.button('确定'):
		if len(nm) > 0:
			nodes = list(node_matcher.match(nm))
			st.text('查询结果为：')
			st.write(nodes)
		else:
			st.warning('请输入数据！')


def find_relation():
	st.header('根据节点查询关系')
	rl_lab1 = st.text_input('请输入需要查询关系节点的标签', key='relation1')
	rl_nm1 = st.text_input('请输入需要查询关系节点的名称', key='name1')
	rl_lab2 = st.text_input('请输入需要查询关系节点的标签', key='relation2')
	rl_nm2 = st.text_input('请输入需要查询关系节点的名称', key='name2')
	if st.button('确定'):
		if len(rl_nm1) != 0 and len(rl_nm2) != 0 and len(rl_lab1) != 0 and len(rl_lab2) != 0:
			node_matcher = NodeMatcher(graph)
			node1 = node_matcher.match(rl_lab1).where(name=rl_nm1).first()
			node2 = node_matcher.match(rl_lab2).where(name=rl_nm2).first()
			if node1 is not None and node2 is not None:
				relationship_matcher = RelationshipMatcher(graph)
				relationship1 = list(relationship_matcher.match((node2, node1), r_type=None))
				relationship2 = list(relationship_matcher.match((node1, node2), r_type=None))
				if len(relationship1) == 0 and len(relationship2) == 0:
					st.write('能力不足，我也查不到了！')
				else:
					if len(relationship2) == 0:
						st.write('查询结果为：' + str(relationship1))
					elif len(relationship1) == 0:
						st.write('查询结果为：' + str(relationship2))
			else:
				st.write('能力不足，我也查不到了！')
		else:
			st.warning('请输入数据！')


def re_find_nm():
	st.header('根据关系查询节点')
	rel = st.text_input('请输入关系')
	if st.button('确定'):
		if len(rel) != 0:
			relationship_matcher = RelationshipMatcher(graph)
			relationships = list(relationship_matcher.match(None, r_type=rel))
			st.write('查询结果为:')
			result = (' ,'.join(str(i) for i in relationships))
			res = result.split(',')
			for s in res:
				a = s.replace(':', '').replace('{}', '')
				st.write(a)
		else:
			st.warning('请输入数据！')


def mother_find_all_son():
	st.header("根据查询所有分支节点")
	la = st.text_input('请输入需要母节点的标签：', key='lab')
	na = st.text_input('请输入需要母节点的名称：', key='name')
	if st.button('确定'):
		if len(la) != 0 and len(na) != 0:
			node_matcher = NodeMatcher(graph)
			relationship_matcher = RelationshipMatcher(graph)
			node1 = node_matcher.match(la).where(name=na).first()
			if node1 is not None:
				result_all = list(relationship_matcher.match([node1], r_type=None))
				st.write('查询结果为：')
				result1 = (' ,'.join(str(i) for i in result_all))
				result2 = result1.split(',')
				for res in result2:
					res2 = res.replace(':', '').replace('{}', '')
					st.write(res2)
			else:
				st.write('能力不足，我也查不到了！')
		else:
			st.warning('请输入数据！')


st.set_page_config(page_title="知识图谱neo4j图形构建", layout="wide")
menu = '''
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
'''
st.markdown(menu, unsafe_allow_html=True)

with st.sidebar:
	choose = option_menu("neo4j数据库操作", ["导入csv文件", "增加", "删除", "修改", "查询"],
						 icons=['house', 'file-earmark-music', 'bar-chart', 'translate', 'brightness-high'],
						 default_index=0)

if choose == "增加":
	select1 = option_menu(None, ["增加节点", "增加关系"],
						  icons=['house', 'file-earmark-music'],
						  menu_icon="cast", default_index=0, orientation="horizontal")
	if select1 == "增加关系":
		insert_relation()
	elif select1 == "增加节点":
		insert()

elif choose == "删除":
	select2 = option_menu(None, ["删除节点", "删除关系", "删库跑路喽！"],
						  icons=['house', 'file-earmark-music', 'bar-chart'],
						  menu_icon="cast", default_index=0, orientation="horizontal")
	if select2 == "删除节点":
		delete()
	elif select2 == "删除关系":
		delete_relation()
	elif select2 == '删库跑路喽！':
		delete_all()

elif choose == "修改":
	select3 = option_menu(None, ["修改节点"],
						  icons=['house'],
						  default_index=0,
						  orientation="horizontal")
	if select3 == "修改节点":
		update()

elif choose == "查询":
	select4 = option_menu(None, ["根据标签查询节点", "根据节点查询关系", "根据关系查询所有节点", "根据查询所有分支节点"],
						  icons=['house', 'file-earmark-music', 'bar-chart', 'translate'],
						  menu_icon="cast", default_index=0, orientation="horizontal")
	if select4 == "根据节点查询关系":
		find_relation()
	elif select4 == "根据标签查询节点":
		find()
	elif select4 == "根据关系查询所有节点":
		re_find_nm()
	elif select4 == "根据查询所有分支节点":
		mother_find_all_son()

elif choose == "导入csv文件":
	import_csv()
