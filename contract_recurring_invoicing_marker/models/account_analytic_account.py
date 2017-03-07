# -*- coding: utf-8 -*-
# (c) 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from dateutil.relativedelta import relativedelta
from babel.dates import format_date
from datetime import date


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def _prepare_invoice(self, contract):
        next_date = fields.Date.from_string(
            contract.recurring_next_date or fields.Date.today())
        interval = 2
        old_date = next_date
        if contract.recurring_rule_type == 'daily':
            new_date = next_date + relativedelta(days=interval - 1)
        elif contract.recurring_rule_type == 'weekly':
            new_date = next_date + relativedelta(weeks=interval, days=-1)
        else:
            new_date = next_date + relativedelta(months=interval, days=-1)
        obj = self.with_context(old_date=old_date, next_date=new_date)
        return super(AccountAnalyticAccount, obj)._prepare_invoice(contract)

    @api.model
    def _insert_markers(self, line, date_start, date_end, date_format):
	lang_obj = self.env['res.lang']
	contract = line.analytic_account_id
	lang = lang_obj.search(
		[('code', '=', contract.partner_id.lang)])
        line = line.replace('#START#', date_start.strftime(date_format))
        line = line.replace('#END#', date_end.strftime(date_format))
        # Invoiced period  need to start to next month
        date_start = date(2017, int(date_start.strftime( '%m' )) +1 , 1 )
	try: 
		lang
	except NameError:
			lang='it'
        line = line.replace('#START_MONTH#', format_date(date_start, "MMMM" , locale=lang).upper())
        line = line.replace('#END_MONTH#', format_date(date_end, "MMMM" , locale=lang).upper())
        return line

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        if 'old_date' in self.env.context and 'next_date' in self.env.context:
            lang_obj = self.env['res.lang']
            contract = line.analytic_account_id
            lang = lang_obj.search(
                [('code', '=', contract.partner_id.lang)])
            date_format = lang.date_format or '%m/%d/%Y'
            res['name'] = self._insert_markers(
                res['name'], self.env.context['old_date'],
                self.env.context['next_date'], date_format)
        return res
