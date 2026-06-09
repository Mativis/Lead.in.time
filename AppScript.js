/**
 * Google Apps Script para transformar a planilha Google no Banco de Dados (API)
 * do Sistema de Leads.
 * 
 * INSTRUÇÕES DE IMPLANTAÇÃO:
 * 1. Na planilha do Google, acesse Extensões > Apps Script.
 * 2. Substitua qualquer código por este conteúdo.
 * 3. Altere o valor da variável AUTH_TOKEN abaixo para um token de sua preferência.
 * 4. Salve o arquivo (ícone do disquete).
 * 5. Clique em "Implantar" (canto superior direito) > "Nova implantação".
 * 6. Em "Selecione o tipo", clique na engrenagem e selecione "Aplicativo da Web".
 * 7. Configure as opções:
 *    - Descrição: API CRM Leads
 *    - Executar como: Eu (seu-email@gmail.com)
 *    - Quem tem acesso: Qualquer pessoa (necessário para o Python conectar, 
 *      mas o token de autenticação cuidará da segurança e impedirá invasões)
 * 8. Clique em "Implantar" e autorize as permissões da sua conta.
 * 9. Copie a URL do Aplicativo da Web gerada (ex: https://script.google.com/macros/s/.../exec).
 * 10. Cole a URL e o seu AuthToken no painel de setup inicial do Streamlit.
 */

// DEFINA AQUI SUA CHAVE DE SEGURANÇA (TOKEN)
const AUTH_TOKEN = "LEAD_IN_TIME_SECRET_TOKEN";

// Adicionar menu especial na planilha ao abrir
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Sistema de Leads')
      .addItem('Configurar Banco de Dados', 'setupDatabase')
      .addToUi();
}

// Configura as abas iniciais e cabeçalhos da planilha
function setupDatabase() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var ui = SpreadsheetApp.getUi();
  
  try {
    // 1. Configuração da aba 'leads'
    var leadsSheet = ss.getSheetByName('leads');
    if (!leadsSheet) {
      leadsSheet = ss.insertSheet('leads');
      var headers = [
        'ID', 'Nome', 'Data Contato', 'Material de Interesse', 'Valor', 
        'Status Consulta', 'Status Cirurgia', 'Observações', 
        'Criado Por', 'Criado Em', 'Atualizado Por', 'Atualizado Em'
      ];
      leadsSheet.appendRow(headers);
      leadsSheet.getRange(1, 1, 1, headers.length)
        .setBackground('#1e293b')
        .setFontColor('#ffffff')
        .setFontWeight('bold')
        .setHorizontalAlignment('center');
      leadsSheet.getRange("E:E").setNumberFormat("R$ #,##0.00");
      for (var i = 1; i <= headers.length; i++) leadsSheet.autoResizeColumn(i);
    }
    
    // 2. Configuração da aba 'users'
    var usersSheet = ss.getSheetByName('users');
    if (!usersSheet) {
      usersSheet = ss.insertSheet('users');
      var headers = ['Username', 'Nome', 'Password Hash', 'Role'];
      usersSheet.appendRow(headers);
      usersSheet.getRange(1, 1, 1, headers.length)
        .setBackground('#1e293b')
        .setFontColor('#ffffff')
        .setFontWeight('bold')
        .setHorizontalAlignment('center');
      
      // admin / admin123
      usersSheet.appendRow(['admin', 'Administrador', '0cd195c0ba4669ce8f34efa93097a8a7230be3b3f26e34755c379e1594b08e0d', 'Admin']);
      // user / user123
      usersSheet.appendRow(['user', 'Usuário Padrão', 'bbdfbb133d3f95fb94f8a369b5b4cbda87d33fb9087c76000a75b7b77cfefc2c', 'User']);
      for (var i = 1; i <= headers.length; i++) usersSheet.autoResizeColumn(i);
    }
    
    // 3. Configuração da aba 'logs'
    var logsSheet = ss.getSheetByName('logs');
    if (!logsSheet) {
      logsSheet = ss.insertSheet('logs');
      var headers = [
        'Data/Hora', 'Usuário', 'Ação', 'ID do Lead', 
        'Descrição Detalhada', 'Campo Alterado', 'Valor Antigo', 'Valor Novo'
      ];
      logsSheet.appendRow(headers);
      logsSheet.getRange(1, 1, 1, headers.length)
        .setBackground('#1e293b')
        .setFontColor('#ffffff')
        .setFontWeight('bold')
        .setHorizontalAlignment('center');
      for (var i = 1; i <= headers.length; i++) logsSheet.autoResizeColumn(i);
    }
    
    // Remover aba inicial vazia
    var defaultSheet = ss.getSheetByName('Página 1') || ss.getSheetByName('Sheet1');
    if (defaultSheet && defaultSheet.getLastRow() === 0 && ss.getSheets().length > 1) {
      ss.deleteSheet(defaultSheet);
    }
    
    ui.alert('Sucesso!', 'Planilha estruturada como banco de dados. Usuários de teste admin/admin123 e user/user123 prontos.', ui.ButtonSet.OK);
  } catch (error) {
    ui.alert('Erro', 'Erro ao configurar: ' + error.message, ui.ButtonSet.OK);
  }
}

// Handler de Requisição HTTP POST
function doPost(e) {
  var responseHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  };

  try {
    var requestData = JSON.parse(e.postData.contents);
    
    // Validação do Token de Segurança
    if (requestData.token !== AUTH_TOKEN) {
      return ContentService.createTextOutput(JSON.stringify({success: false, error: "Token de autenticação inválido ou não informado."}))
                           .setMimeType(ContentService.MimeType.JSON);
    }
    
    var action = requestData.action;
    var payload = requestData.payload || {};
    var result = {};
    
    switch (action) {
      case "getLeads":
        result = {success: true, data: getLeads()};
        break;
      case "addLead":
        result = addLead(payload);
        break;
      case "updateLead":
        result = updateLead(payload);
        break;
      case "deleteLead":
        result = deleteLead(payload);
        break;
      case "getUsers":
        result = {success: true, data: getUsers()};
        break;
      case "addUser":
        result = addUser(payload);
        break;
      case "changePassword":
        result = changePassword(payload);
        break;
      case "getLogs":
        result = {success: true, data: getLogs()};
        break;
      default:
        result = {success: false, error: "Ação '" + action + "' não reconhecida."};
    }
    
    return ContentService.createTextOutput(JSON.stringify(result))
                         .setMimeType(ContentService.MimeType.JSON);
                         
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({success: false, error: err.message}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

// Permite a resposta de CORS OPTIONS pré-vôos no navegador, se necessário
function doOptions(e) {
  return ContentService.createTextOutput("")
                       .setMimeType(ContentService.MimeType.TEXT);
}

// --- FUNÇÕES DE TRANSAÇÃO DO BANCO ---

function getLeads() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('leads');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];
  
  var headers = data[0];
  var list = [];
  for (var i = 1; i < data.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = data[i][j];
    }
    list.push(obj);
  }
  return list;
}

function addLead(payload) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('leads');
  if (!sheet) return {success: false, error: "Aba 'leads' não configurada."};
  
  var leadId = Utilities.getUuid();
  var timestamp = Utilities.formatDate(new Date(), "GMT-3", "dd-MM-yyyy HH:mm:ss");
  
  var row = [
    leadId,
    payload.nome,
    payload.data_contato,
    payload.material,
    parseFloat(payload.valor),
    payload.status_consulta,
    payload.status_cirurgia,
    payload.observacoes,
    payload.criado_por,
    timestamp,
    payload.criado_por,
    timestamp
  ];
  
  sheet.appendRow(row);
  
  // Registrar log
  logAction(
    payload.criado_por, 
    "CRIAR", 
    leadId, 
    "Lead '" + payload.nome + "' criado com Status Consulta '" + payload.status_consulta + "' e Cirurgia '" + payload.status_cirurgia + "'",
    "", "", ""
  );
  
  return {success: true, id: leadId};
}

function updateLead(payload) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('leads');
  if (!sheet) return {success: false, error: "Aba 'leads' não configurada."};
  
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var leadId = payload.lead_id;
  var updatedFields = payload.updated_data;
  var user = payload.user;
  
  var rowIdx = -1;
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == leadId) {
      rowIdx = i + 1;
      break;
    }
  }
  
  if (rowIdx === -1) {
    return {success: false, error: "Lead não encontrado para atualização."};
  }
  
  var timestamp = Utilities.formatDate(new Date(), "GMT-3", "dd-MM-yyyy HH:mm:ss");
  var oldRow = data[rowIdx - 1];
  
  // Criar mapeamento do cabeçalho
  var headerMap = {};
  for (var j = 0; j < headers.length; j++) {
    headerMap[headers[j]] = j + 1;
  }
  
  var changes = [];
  for (var key in updatedFields) {
    var col = headerMap[key];
    if (col) {
      var oldVal = oldRow[col - 1];
      var newVal = updatedFields[key];
      
      if (key === "Valor") {
        var oldValFloat = parseFloat(oldVal) || 0;
        var newValFloat = parseFloat(newVal) || 0;
        if (oldValFloat !== newValFloat) {
          changes.push({field: key, old: String(oldValFloat), new: String(newValFloat)});
          sheet.getRange(rowIdx, col).setValue(newValFloat);
        }
      } else {
        var oldValStr = String(oldVal).trim();
        var newValStr = String(newVal).trim();
        if (oldValStr !== newValStr) {
          changes.push({field: key, old: oldValStr, new: newValStr});
          sheet.getRange(rowIdx, col).setValue(newValStr);
        }
      }
    }
  }
  
  if (changes.length > 0) {
    sheet.getRange(rowIdx, headerMap["Atualizado Por"]).setValue(user);
    sheet.getRange(rowIdx, headerMap["Atualizado Em"]).setValue(timestamp);
    
    var leadName = updatedFields["Nome"] || oldRow[1];
    for (var k = 0; k < changes.length; k++) {
      logAction(
        user, 
        "EDITAR", 
        leadId, 
        "Alterou o campo '" + changes[k].field + "' do lead '" + leadName + "'", 
        changes[k].field, 
        changes[k].old, 
        changes[k].new
      );
    }
  }
  
  return {success: true};
}

function deleteLead(payload) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('leads');
  if (!sheet) return {success: false, error: "Aba 'leads' não configurada."};
  
  var data = sheet.getDataRange().getValues();
  var leadId = payload.lead_id;
  var leadName = payload.lead_name;
  var user = payload.user;
  
  var rowIdx = -1;
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == leadId) {
      rowIdx = i + 1;
      break;
    }
  }
  
  if (rowIdx === -1) {
    return {success: false, error: "Lead não encontrado para exclusão."};
  }
  
  sheet.deleteRow(rowIdx);
  logAction(user, "EXCLUIR", leadId, "Lead '" + leadName + "' excluído permanentemente do sistema.", "", "", "");
  return {success: true};
}

function getUsers() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('users');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];
  
  var list = [];
  for (var i = 1; i < data.length; i++) {
    list.push({
      Username: data[i][0],
      Nome: data[i][1],
      "Password Hash": data[i][2],
      Role: data[i][3]
    });
  }
  return list;
}

function addUser(payload) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('users');
  if (!sheet) return {success: false, error: "Aba 'users' não configurada."};
  
  var data = sheet.getDataRange().getValues();
  var usernameClean = payload.username.trim().toLowerCase();
  
  for (var i = 1; i < data.length; i++) {
    if (String(data[i][0]).toLowerCase() == usernameClean) {
      return {success: false, error: "Este nome de usuário já está cadastrado."};
    }
  }
  
  sheet.appendRow([usernameClean, payload.nome, payload.pwd_hash, payload.role]);
  logAction(payload.actor, "CRIAR_USUARIO", "-", "Usuário '" + usernameClean + "' (" + payload.role + ") cadastrado por '" + payload.actor + "'.", "", "", "");
  return {success: true};
}

function changePassword(payload) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('users');
  if (!sheet) return {success: false, error: "Aba 'users' não configurada."};
  
  var data = sheet.getDataRange().getValues();
  var usernameClean = payload.username.trim().toLowerCase();
  
  var rowIdx = -1;
  for (var i = 1; i < data.length; i++) {
    if (String(data[i][0]).toLowerCase() == usernameClean) {
      rowIdx = i + 1;
      break;
    }
  }
  
  if (rowIdx === -1) {
    return {success: false, error: "Usuário não encontrado."};
  }
  
  sheet.getRange(rowIdx, 3).setValue(payload.new_hash); // Coluna 3: Password Hash
  return {success: true};
}

function getLogs() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('logs');
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];
  
  var headers = data[0];
  var list = [];
  for (var i = 1; i < data.length; i++) {
    var obj = {};
    for (var j = 0; j < headers.length; j++) {
      obj[headers[j]] = data[i][j];
    }
    list.push(obj);
  }
  return list;
}

function logAction(usuario, acao, leadId, descricao, campoAlterado, valorAntigo, valorNovo) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('logs');
  if (!sheet) return;
  
  var timestamp = Utilities.formatDate(new Date(), "GMT-3", "dd-MM-yyyy HH:mm:ss");
  sheet.appendRow([
    timestamp,
    usuario,
    acao,
    leadId,
    descricao,
    campoAlterado || "",
    valorAntigo || "",
    valorNovo || ""
  ]);
}
