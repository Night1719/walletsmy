(function(){
	function el(tag, attrs={}, children=[]) {
		const e = document.createElement(tag);
		Object.entries(attrs).forEach(([k,v])=>{
			if (k === 'class') e.className = v; else if(k==='text') e.textContent = v; else e.setAttribute(k, v);
		});
		children.forEach(c => e.appendChild(c));
		return e;
	}

	function createQuestionCard(q, idx, onChange){
		const typeSelect = el('select', { class: 'input' }, [
			el('option', { value:'text', text:'Текстовый ответ' }),
			el('option', { value:'single', text:'Один вариант' }),
			el('option', { value:'multiple', text:'Несколько вариантов' }),
		]);
		typeSelect.value = q.qtype || 'single';

		const titleInput = el('input', { class: 'input', placeholder:'Текст вопроса', value: q.text || '' });
		const optionsWrap = el('div', { class: 'q-body' });

		function renderOptions(){
			optionsWrap.innerHTML = '';
			if (typeSelect.value === 'text') return;
			(q.options||[]).forEach((opt, i)=>{
				const inOpt = el('input', { class: 'input', value: opt || '', placeholder: `Вариант ${i+1}` });
				inOpt.addEventListener('input', ()=>{ q.options[i] = inOpt.value; onChange(); });
				const btnDel = el('button', { class:'btn btn-ghost', type:'button', text:'Удалить' });
				btnDel.addEventListener('click', ()=>{ q.options.splice(i,1); renderOptions(); onChange(); });
				optionsWrap.appendChild(el('div', { class:'opt-row' }, [inOpt, btnDel]));
			});
			const btnAdd = el('button', { class:'btn btn-outline', type:'button', text:'Добавить вариант' });
			btnAdd.addEventListener('click', ()=>{ q.options = q.options || []; q.options.push('Новый вариант'); renderOptions(); onChange(); });
			optionsWrap.appendChild(btnAdd);
		}

		const btnUp = el('button', { class:'btn btn-ghost', type:'button', text:'↑' });
		const btnDown = el('button', { class:'btn btn-ghost', type:'button', text:'↓' });
		const btnDelete = el('button', { class:'btn btn-danger', type:'button', text:'Удалить вопрос' });

		const qCard = el('div', { class:'q-card' }, [
			el('div', { class:'q-head' }, [
				el('div', {}, [el('span', { class:'handle', text:'⋮⋮' }), el('span', { text:`Вопрос ${idx+1}` })]),
				el('div', { class:'q-actions' }, [btnUp, btnDown, btnDelete])
			]),
			el('div', { class:'q-body' }, [
				el('div', {}, [ el('label', { class:'label', text:'Формат' }), typeSelect ]),
				el('div', {}, [ el('label', { class:'label', text:'Текст вопроса' }), titleInput ]),
				optionsWrap
			])
		]);

		titleInput.addEventListener('input', ()=>{ q.text = titleInput.value; onChange(); });
		typeSelect.addEventListener('change', ()=>{ if (typeSelect.value !== 'text' && !q.options) q.options = ['Вариант 1']; q.qtype = typeSelect.value; renderOptions(); onChange(); });
		btnDelete.addEventListener('click', ()=>{ onChange({ type:'delete', idx }); });
		btnUp.addEventListener('click', ()=>{ onChange({ type:'move', idx, dir:-1 }); });
		btnDown.addEventListener('click', ()=>{ onChange({ type:'move', idx, dir:1 }); });

		renderOptions();
		return qCard;
	}

	window.Builder = function(container, textarea) {
		let questions = [];
		try { questions = JSON.parse(textarea.value || '[]') } catch(e) { questions = [] }
		function sync(){ textarea.value = JSON.stringify(questions, null, 2); }
		function render(){
			container.innerHTML = '';
			questions.forEach((q, idx)=>{
				container.appendChild(createQuestionCard(q, idx, (evt)=>{
					if (!evt) { sync(); return }
					if (evt.type === 'delete') { questions.splice(evt.idx,1); render(); sync(); return }
					if (evt.type === 'move') {
						const j = evt.idx + evt.dir; if (j<0||j>=questions.length) return;
						const tmp = questions[evt.idx]; questions[evt.idx] = questions[j]; questions[j] = tmp; render(); sync(); return;
					}
					sync();
				}));
			});
			const addRow = el('div', { style:'display:flex; gap:8px; justify-content:flex-end; margin-top:8px;' }, [
				el('button', { class:'btn btn-outline', type:'button', text:'Добавить вопрос' })
			]);
			addRow.firstChild.addEventListener('click', ()=>{ questions.push({ text:'Новый вопрос', qtype:'single', options:['Вариант 1'] }); render(); sync(); });
			container.appendChild(addRow);
		}
		render(); sync();
		return { getQuestions: ()=>questions };
	}
})();