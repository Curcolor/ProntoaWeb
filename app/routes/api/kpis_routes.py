"""
Blueprint de API para KPIs y métricas.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.kpi_service import KPIService

kpis_api_bp = Blueprint('kpis_api', __name__, url_prefix='/api/kpis')


@kpis_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_metrics():
    """Obtiene métricas del dashboard."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        metrics = KPIService.get_dashboard_metrics(current_user.business.id)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo métricas: {str(e)}'
        }), 500


@kpis_api_bp.route('/comparisons', methods=['GET'])
@login_required
def get_kpi_comparisons():
    """Obtiene comparaciones de KPIs."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        period_days = request.args.get('period_days', 30, type=int)
        
        comparisons = KPIService.get_kpi_comparisons(
            current_user.business.id,
            period_days=period_days
        )
        
        return jsonify({
            'success': True,
            'comparisons': comparisons,
            'period_days': period_days
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo comparaciones: {str(e)}'
        }), 500


@kpis_api_bp.route('/operational', methods=['GET'])
@login_required
def get_operational_metrics():
    """Obtiene métricas operativas."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        period_days = request.args.get('period_days', 30, type=int)
        
        metrics = KPIService.get_operational_metrics(
            current_user.business.id,
            period_days=period_days
        )
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'period_days': period_days
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo métricas operativas: {str(e)}'
        }), 500


@kpis_api_bp.route('/financial', methods=['GET'])
@login_required
def get_financial_impact():
    """Obtiene impacto financiero."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        period_days = request.args.get('period_days', 30, type=int)
        
        impact = KPIService.get_financial_impact(
            current_user.business.id,
            period_days=period_days
        )
        
        return jsonify({
            'success': True,
            'impact': impact,
            'period_days': period_days
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo impacto financiero: {str(e)}'
        }), 500


@kpis_api_bp.route('/orders-by-hour', methods=['GET'])
@login_required
def get_orders_by_hour():
    """Obtiene distribución de pedidos por hora."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        days = request.args.get('days', 7, type=int)
        
        distribution = KPIService.get_orders_by_hour(
            current_user.business.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'distribution': distribution,
            'days_analyzed': days
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo distribución: {str(e)}'
        }), 500


@kpis_api_bp.route('/summary', methods=['GET'])
@login_required
def get_complete_summary():
    """Obtiene un resumen completo de todas las métricas."""
    try:
        if not current_user.business:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene un negocio asociado'
            }), 400
        
        period_days = request.args.get('period_days', 30, type=int)
        business_id = current_user.business.id
        
        summary = {
            'dashboard': KPIService.get_dashboard_metrics(business_id),
            'comparisons': KPIService.get_kpi_comparisons(business_id, period_days),
            'operational': KPIService.get_operational_metrics(business_id, period_days),
            'financial': KPIService.get_financial_impact(business_id, period_days),
            'hourly_distribution': KPIService.get_orders_by_hour(business_id, 7)
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'period_days': period_days
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo resumen: {str(e)}'
        }), 500
