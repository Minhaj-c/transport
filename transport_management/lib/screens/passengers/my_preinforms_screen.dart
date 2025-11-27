import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/preinform_model.dart';
import '../../services/api_service.dart';
import '../../widgets/loading_widget.dart' as app_widgets;

class MyPreInformsScreen extends StatefulWidget {
  const MyPreInformsScreen({super.key});

  @override
  State<MyPreInformsScreen> createState() => _MyPreInformsScreenState();
}

class _MyPreInformsScreenState extends State<MyPreInformsScreen> {
  List<PreInform> _preinforms = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPreInforms();
  }

  Future<void> _loadPreInforms() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final preinforms = await ApiService.getMyPreInforms();
      setState(() {
        _preinforms = preinforms;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _cancelPreInform(PreInform preinform) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Pre-Inform'),
        content:
            const Text('Are you sure you want to cancel this pre-inform?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text(
              'Yes, Cancel',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await ApiService.cancelPreInform(preinform.id);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Pre-inform cancelled'),
          backgroundColor: Colors.orange,
        ),
      );

      _loadPreInforms();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to cancel: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const app_widgets.LoadingWidget(
        message: 'Loading your pre-informs...',
      );
    }

    if (_error != null) {
      return app_widgets.ErrorWidget(
        message: _error!,
        onRetry: _loadPreInforms,
      );
    }

    if (_preinforms.isEmpty) {
      return const app_widgets.EmptyWidget(
        message: 'No pre-informs yet\nTap on a route to create one',
        icon: Icons.notifications_none,
      );
    }

    return RefreshIndicator(
      onRefresh: _loadPreInforms,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _preinforms.length,
        itemBuilder: (context, index) {
          final preinform = _preinforms[index];
          return _PreInformCard(
            preinform: preinform,
            onCancel: () => _cancelPreInform(preinform),
          );
        },
      ),
    );
  }
}

class _PreInformCard extends StatelessWidget {
  final PreInform preinform;
  final VoidCallback onCancel;

  const _PreInformCard({
    required this.preinform,
    required this.onCancel,
  });

  Color _getStatusColor() {
    switch (preinform.status) {
      case 'pending':
        return Colors.orange;
      case 'noted':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon() {
    switch (preinform.status) {
      case 'pending':
        return Icons.pending;
      case 'noted':
        return Icons.check_circle_outline;
      case 'completed':
        return Icons.check_circle;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.info;
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('MMM dd, yyyy');
    final isPending = preinform.status == 'pending';
    final isFuture = preinform.dateOfTravel.isAfter(DateTime.now());

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _getStatusColor().withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _getStatusIcon(),
                        size: 16,
                        color: _getStatusColor(),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        preinform.statusText,
                        style: TextStyle(
                          color: _getStatusColor(),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isPending && isFuture)
                  IconButton(
                    icon: const Icon(Icons.cancel, color: Colors.red),
                    onPressed: onCancel,
                    tooltip: 'Cancel',
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // Route Name
            Text(
              preinform.routeName,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),

            // Date
            Row(
              children: [
                const Icon(Icons.calendar_today, size: 16),
                const SizedBox(width: 8),
                Text(
                  dateFormat.format(preinform.dateOfTravel),
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Time
            Row(
              children: [
                const Icon(Icons.access_time, size: 16),
                const SizedBox(width: 8),
                Text(
                  preinform.desiredTime,
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Stop
            Row(
              children: [
                const Icon(Icons.location_on, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    preinform.stopName,
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Passengers
            Row(
              children: [
                const Icon(Icons.people, size: 16),
                const SizedBox(width: 8),
                Text(
                  '${preinform.passengerCount} passenger${preinform.passengerCount > 1 ? 's' : ''}',
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Created At
            Text(
              'Created ${_formatCreatedAt(preinform.createdAt)}',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatCreatedAt(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 0) {
      return '${difference.inDays} day${difference.inDays > 1 ? 's' : ''} ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} hour${difference.inHours > 1 ? 's' : ''} ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} minute${difference.inMinutes > 1 ? 's' : ''} ago';
    } else {
      return 'Just now';
    }
  }
}
