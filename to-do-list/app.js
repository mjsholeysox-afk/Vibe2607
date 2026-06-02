(function(){
  const keyBase = 'todo-today-';
  const today = new Date();
  const todayKey = keyBase + today.toISOString().slice(0,10);

  const els = {
    date: document.getElementById('today-date'),
    form: document.getElementById('task-form'),
    title: document.getElementById('task-title'),
    note: document.getElementById('task-note'),
    priority: document.getElementById('task-priority'),
    list: document.getElementById('task-list'),
    filters: document.querySelectorAll('.filter-btn'),
    counts: document.getElementById('counts')
  };

  let tasks = loadTasks();
  let filter = 'all';

  function fmtDate(d){
    return d.toLocaleDateString('ko-KR', {weekday:'short', year:'numeric', month:'numeric', day:'numeric'});
  }

  function saveTasks(){
    localStorage.setItem(todayKey, JSON.stringify(tasks));
  }

  function loadTasks(){
    try{
      const raw = localStorage.getItem(todayKey);
      return raw ? JSON.parse(raw) : [];
    }catch(e){
      console.error(e);return [];
    }
  }

  function uid(){return Date.now().toString(36)+Math.random().toString(36).slice(2,7)}

  function addTask(title,note,priority){
    const t = {id:uid(),title:title.trim(),note:note||'',priority:priority||'normal',completed:false,created:Date.now()};
    tasks.push(t); saveTasks(); render();
  }

  function deleteTask(id){
    tasks = tasks.filter(t=>t.id!==id); saveTasks(); render();
  }

  function toggleComplete(id){
    const it = tasks.find(t=>t.id===id); if(!it) return; it.completed = !it.completed; saveTasks(); render();
  }

  function editTask(id){
    const it = tasks.find(t=>t.id===id); if(!it) return;
    const newTitle = prompt('항목 제목을 수정하세요', it.title);
    if(newTitle===null) return;
    it.title = newTitle.trim() || it.title;
    const newNote = prompt('메모를 수정하세요 (빈칸은 유지)', it.note);
    if(newNote!==null) it.note = newNote;
    saveTasks(); render();
  }

  function setFilter(f){ filter=f; els.filters.forEach(b=> b.setAttribute('aria-pressed', b.dataset.filter===f)); render(); }

  function render(){
    els.list.innerHTML='';
    const visible = tasks.filter(t=>{
      if(filter==='all') return true;
      if(filter==='active') return !t.completed;
      if(filter==='completed') return t.completed;
    });

    // sort: incomplete first, then by priority high->normal->low, then created
    const priorityOrder = {high:0,normal:1,low:2};
    visible.sort((a,b)=> (a.completed - b.completed) || (priorityOrder[a.priority]-priorityOrder[b.priority]) || (a.created - b.created));

    visible.forEach(t=>{
      const li = document.createElement('li'); li.className='task-item'+(t.completed ? ' completed':''); li.dataset.id=t.id;

      const cb = document.createElement('input'); cb.type='checkbox'; cb.checked = !!t.completed; cb.setAttribute('aria-label','완료 토글'); cb.className='cb';
      cb.addEventListener('change', ()=> toggleComplete(t.id));

      const title = document.createElement('div'); title.className='title'; title.tabIndex=0; title.textContent = t.title;
      title.addEventListener('dblclick', ()=> editTask(t.id));
      title.addEventListener('keydown', (e)=>{ if(e.key==='Enter') editTask(t.id); });

      const badge = document.createElement('div'); badge.className = 'badge '+t.priority; badge.textContent = t.priority==='high' ? '높음' : t.priority==='normal' ? '보통' : '낮음';

      const editBtn = document.createElement('button'); editBtn.className='btn'; editBtn.title='편집'; editBtn.innerText='✏️'; editBtn.addEventListener('click', ()=> editTask(t.id));
      const delBtn = document.createElement('button'); delBtn.className='btn'; delBtn.title='삭제'; delBtn.innerText='🗑️'; delBtn.addEventListener('click', ()=> { if(confirm('삭제하시겠습니까?')) deleteTask(t.id); });

      li.appendChild(cb);
      li.appendChild(title);
      li.appendChild(badge);
      li.appendChild(editBtn);
      li.appendChild(delBtn);

      els.list.appendChild(li);
    });

    const total = tasks.length; const completed = tasks.filter(t=>t.completed).length; const active = total - completed;
    els.counts.textContent = `전체 ${total} • 미완료 ${active} • 완료 ${completed}`;
  }

  // 초기화
  els.date.textContent = fmtDate(today);
  els.form.addEventListener('submit', (e)=>{
    e.preventDefault(); const title = els.title.value; if(!title.trim()) return; addTask(title, els.note.value, els.priority.value); els.form.reset(); els.title.focus();
  });

  els.filters.forEach(b=> b.addEventListener('click', ()=> setFilter(b.dataset.filter)));

  // 키보드: Enter로 제목 입력 시 제출
  els.title.addEventListener('keydown', (e)=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); els.form.requestSubmit(); }});

  render();
})();
